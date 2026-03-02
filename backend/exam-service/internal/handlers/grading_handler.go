package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/openzhixue/exam-service/internal/models"
	"github.com/openzhixue/exam-service/internal/services"
)

type GradingHandler struct {
	gradingService *services.GradingService
}

func NewGradingHandler(gradingService *services.GradingService) *GradingHandler {
	return &GradingHandler{
		gradingService: gradingService,
	}
}

func (h *GradingHandler) GradeAnswer(c *gin.Context) {
	examIDStr := c.Param("id")
	_, err := uuid.Parse(examIDStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	var req models.GradeAnswerRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		ValidationError(c, err)
		return
	}

	userID, exists := c.Get("userID")
	if !exists {
		Unauthorized(c, "user not authenticated")
		return
	}

	graderID, ok := userID.(uuid.UUID)
	if !ok {
		BadRequest(c, "invalid user id")
		return
	}

	response, err := h.gradingService.GradeAnswer(c.Request.Context(), &req, graderID)
	if err != nil {
		switch err {
		case services.ErrSessionNotFound:
			NotFound(c, "session not found")
			return
		case services.ErrAnswerNotFound:
			NotFound(c, "answer not found")
			return
		case services.ErrCannotGrade:
			Forbidden(c, "cannot grade answer in current state")
			return
		case services.ErrInvalidScore:
			BadRequest(c, "invalid score")
			return
		default:
			InternalError(c, err.Error())
			return
		}
	}

	Success(c, response)
}

func (h *GradingHandler) AutoGradeSession(c *gin.Context) {
	sessionIDStr := c.Param("sessionId")
	sessionID, err := uuid.Parse(sessionIDStr)
	if err != nil {
		BadRequest(c, "invalid session id")
		return
	}

	if err := h.gradingService.AutoGradeSession(c.Request.Context(), sessionID); err != nil {
		if err == services.ErrSessionNotFound {
			NotFound(c, "session not found")
			return
		}
		if err == services.ErrCannotGrade {
			Forbidden(c, "cannot grade session in current state")
			return
		}
		InternalError(c, err.Error())
		return
	}

	SuccessWithMessage(c, "auto grading completed", nil)
}

func (h *GradingHandler) GetStudentResult(c *gin.Context) {
	sessionIDStr := c.Param("sessionId")
	sessionID, err := uuid.Parse(sessionIDStr)
	if err != nil {
		BadRequest(c, "invalid session id")
		return
	}

	result, err := h.gradingService.GetStudentResult(c.Request.Context(), sessionID)
	if err != nil {
		NotFound(c, "result not found")
		return
	}

	Success(c, result)
}
