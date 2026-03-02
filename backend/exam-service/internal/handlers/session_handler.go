package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/openzhixue/exam-service/internal/models"
	"github.com/openzhixue/exam-service/internal/services"
)

type SessionHandler struct {
	sessionService *services.SessionService
	gradingService *services.GradingService
}

func NewSessionHandler(sessionService *services.SessionService, gradingService *services.GradingService) *SessionHandler {
	return &SessionHandler{
		sessionService: sessionService,
		gradingService: gradingService,
	}
}

func (h *SessionHandler) StartExam(c *gin.Context) {
	examIDStr := c.Param("id")
	examID, err := uuid.Parse(examIDStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	userID, exists := c.Get("userID")
	if !exists {
		Unauthorized(c, "user not authenticated")
		return
	}

	studentID, ok := userID.(uuid.UUID)
	if !ok {
		BadRequest(c, "invalid user id")
		return
	}

	var req models.SessionStartRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		req = models.SessionStartRequest{
			IPAddress: c.ClientIP(),
			UserAgent: c.GetHeader("User-Agent"),
		}
	}

	session, err := h.sessionService.StartExam(c.Request.Context(), examID, studentID, &req)
	if err != nil {
		switch err {
		case services.ErrExamNotFound:
			NotFound(c, "exam not found")
			return
		case services.ErrExamNotPublished:
			Forbidden(c, "exam is not published")
			return
		case services.ErrExamNotStarted:
			Forbidden(c, "exam has not started")
			return
		case services.ErrExamEnded:
			Forbidden(c, "exam has ended")
			return
		case services.ErrSessionSubmitted:
			Forbidden(c, "exam already submitted")
			return
		default:
			InternalError(c, err.Error())
			return
		}
	}

	Created(c, session)
}

func (h *SessionHandler) GetSession(c *gin.Context) {
	sessionIDStr := c.Param("sessionId")
	sessionID, err := uuid.Parse(sessionIDStr)
	if err != nil {
		BadRequest(c, "invalid session id")
		return
	}

	response, err := h.sessionService.GetSessionWithQuestions(c.Request.Context(), sessionID)
	if err != nil {
		NotFound(c, "session not found")
		return
	}

	Success(c, response)
}

func (h *SessionHandler) GetExamQuestions(c *gin.Context) {
	examIDStr := c.Param("id")
	examID, err := uuid.Parse(examIDStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	userID, exists := c.Get("userID")
	if !exists {
		Unauthorized(c, "user not authenticated")
		return
	}

	studentID, ok := userID.(uuid.UUID)
	if !ok {
		BadRequest(c, "invalid user id")
		return
	}

	session, err := h.sessionService.GetSessionByExamAndStudent(c.Request.Context(), examID, studentID)
	if err != nil {
		NotFound(c, "session not found")
		return
	}

	response, err := h.sessionService.GetSessionWithQuestions(c.Request.Context(), session.ID)
	if err != nil {
		InternalError(c, err.Error())
		return
	}

	Success(c, response)
}

func (h *SessionHandler) SubmitAnswer(c *gin.Context) {
	examIDStr := c.Param("id")
	examID, err := uuid.Parse(examIDStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	userID, exists := c.Get("userID")
	if !exists {
		Unauthorized(c, "user not authenticated")
		return
	}

	studentID, ok := userID.(uuid.UUID)
	if !ok {
		BadRequest(c, "invalid user id")
		return
	}

	var req models.AnswerSubmitRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		ValidationError(c, err)
		return
	}

	session, err := h.sessionService.GetSessionByExamAndStudent(c.Request.Context(), examID, studentID)
	if err != nil {
		NotFound(c, "session not found")
		return
	}

	if err := h.sessionService.SubmitAnswer(c.Request.Context(), session.ID, &req); err != nil {
		if err == services.ErrSessionExpired {
			Forbidden(c, "session has expired")
			return
		}
		if err == services.ErrSessionSubmitted {
			Forbidden(c, "session already submitted")
			return
		}
		InternalError(c, err.Error())
		return
	}

	SuccessWithMessage(c, "answer submitted", nil)
}

func (h *SessionHandler) SubmitExam(c *gin.Context) {
	examIDStr := c.Param("id")
	examID, err := uuid.Parse(examIDStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	userID, exists := c.Get("userID")
	if !exists {
		Unauthorized(c, "user not authenticated")
		return
	}

	studentID, ok := userID.(uuid.UUID)
	if !ok {
		BadRequest(c, "invalid user id")
		return
	}

	var req models.SessionSubmitRequest
	c.ShouldBindJSON(&req)

	session, err := h.sessionService.GetSessionByExamAndStudent(c.Request.Context(), examID, studentID)
	if err != nil {
		NotFound(c, "session not found")
		return
	}

	if err := h.sessionService.SubmitExam(c.Request.Context(), session.ID, req.Force); err != nil {
		if err == services.ErrSessionExpired {
			Forbidden(c, "session has expired")
			return
		}
		if err == services.ErrSessionSubmitted {
			Forbidden(c, "session already submitted")
			return
		}
		InternalError(c, err.Error())
		return
	}

	if err := h.gradingService.AutoGradeSession(c.Request.Context(), session.ID); err != nil {
		InternalError(c, err.Error())
		return
	}

	SuccessWithMessage(c, "exam submitted successfully", nil)
}

func (h *SessionHandler) GetExamResult(c *gin.Context) {
	examIDStr := c.Param("id")
	examID, err := uuid.Parse(examIDStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	userID, exists := c.Get("userID")
	if !exists {
		Unauthorized(c, "user not authenticated")
		return
	}

	studentID, ok := userID.(uuid.UUID)
	if !ok {
		BadRequest(c, "invalid user id")
		return
	}

	session, err := h.sessionService.GetSessionByExamAndStudent(c.Request.Context(), examID, studentID)
	if err != nil {
		NotFound(c, "session not found")
		return
	}

	result, err := h.gradingService.GetStudentResult(c.Request.Context(), session.ID)
	if err != nil {
		InternalError(c, err.Error())
		return
	}

	Success(c, result)
}
