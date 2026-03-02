package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/openzhixue/exam-service/internal/models"
	"github.com/openzhixue/exam-service/internal/services"
)

type ExamHandler struct {
	examService *services.ExamService
}

func NewExamHandler(examService *services.ExamService) *ExamHandler {
	return &ExamHandler{
		examService: examService,
	}
}

func (h *ExamHandler) CreateExam(c *gin.Context) {
	var req models.ExamCreateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		ValidationError(c, err)
		return
	}

	userID, exists := c.Get("userID")
	if !exists {
		Unauthorized(c, "user not authenticated")
		return
	}

	creatorID, ok := userID.(uuid.UUID)
	if !ok {
		BadRequest(c, "invalid user id")
		return
	}

	exam, err := h.examService.CreateExam(c.Request.Context(), &req, creatorID)
	if err != nil {
		InternalError(c, err.Error())
		return
	}

	Created(c, exam)
}

func (h *ExamHandler) GetExam(c *gin.Context) {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	exam, err := h.examService.GetExam(c.Request.Context(), id)
	if err != nil {
		NotFound(c, "exam not found")
		return
	}

	Success(c, exam)
}

func (h *ExamHandler) GetExamDetail(c *gin.Context) {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	exam, questions, err := h.examService.GetExamWithQuestions(c.Request.Context(), id)
	if err != nil {
		NotFound(c, "exam not found")
		return
	}

	Success(c, gin.H{
		"exam":      exam,
		"questions": questions,
	})
}

func (h *ExamHandler) ListExams(c *gin.Context) {
	var filter models.ExamFilter
	if err := c.ShouldBindQuery(&filter); err != nil {
		ValidationError(c, err)
		return
	}

	if filter.Page == 0 {
		filter.Page = 1
	}
	if filter.PageSize == 0 {
		filter.PageSize = 10
	}

	response, err := h.examService.ListExams(c.Request.Context(), &filter)
	if err != nil {
		InternalError(c, err.Error())
		return
	}

	Success(c, response)
}

func (h *ExamHandler) UpdateExam(c *gin.Context) {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	var req models.ExamUpdateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		ValidationError(c, err)
		return
	}

	exam, err := h.examService.UpdateExam(c.Request.Context(), id, &req)
	if err != nil {
		if err == services.ErrExamCannotModify {
			Forbidden(c, "exam cannot be modified in current status")
			return
		}
		NotFound(c, "exam not found")
		return
	}

	Success(c, exam)
}

func (h *ExamHandler) DeleteExam(c *gin.Context) {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	if err := h.examService.DeleteExam(c.Request.Context(), id); err != nil {
		if err == services.ErrExamCannotDelete {
			Forbidden(c, "exam cannot be deleted in current status")
			return
		}
		NotFound(c, "exam not found")
		return
	}

	NoContent(c)
}

func (h *ExamHandler) PublishExam(c *gin.Context) {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	if err := h.examService.PublishExam(c.Request.Context(), id); err != nil {
		if err == services.ErrExamCannotPublish {
			Forbidden(c, "exam cannot be published")
			return
		}
		if err == services.ErrNoQuestions {
			BadRequest(c, "exam has no questions")
			return
		}
		NotFound(c, "exam not found")
		return
	}

	SuccessWithMessage(c, "exam published successfully", nil)
}
