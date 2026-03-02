package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/openzhixue/exam-service/internal/models"
	"github.com/openzhixue/exam-service/internal/services"
)

type QuestionHandler struct {
	questionService *services.QuestionService
}

func NewQuestionHandler(questionService *services.QuestionService) *QuestionHandler {
	return &QuestionHandler{
		questionService: questionService,
	}
}

func (h *QuestionHandler) CreateQuestion(c *gin.Context) {
	var req models.QuestionCreateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		ValidationError(c, err)
		return
	}

	question, err := h.questionService.CreateQuestion(c.Request.Context(), &req)
	if err != nil {
		if err == services.ErrExamNotFound {
			NotFound(c, "exam not found")
			return
		}
		if err == services.ErrExamCannotModify {
			Forbidden(c, "exam cannot be modified in current status")
			return
		}
		InternalError(c, err.Error())
		return
	}

	Created(c, question)
}

func (h *QuestionHandler) CreateQuestionsBatch(c *gin.Context) {
	var req models.QuestionBatchCreateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		ValidationError(c, err)
		return
	}

	questions, err := h.questionService.CreateQuestionsBatch(c.Request.Context(), &req)
	if err != nil {
		if err == services.ErrExamNotFound {
			NotFound(c, "exam not found")
			return
		}
		if err == services.ErrExamCannotModify {
			Forbidden(c, "exam cannot be modified in current status")
			return
		}
		InternalError(c, err.Error())
		return
	}

	Created(c, questions)
}

func (h *QuestionHandler) GetQuestion(c *gin.Context) {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		BadRequest(c, "invalid question id")
		return
	}

	question, err := h.questionService.GetQuestion(c.Request.Context(), id)
	if err != nil {
		NotFound(c, "question not found")
		return
	}

	Success(c, question)
}

func (h *QuestionHandler) GetQuestionsByExam(c *gin.Context) {
	examIDStr := c.Param("examId")
	examID, err := uuid.Parse(examIDStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	questions, err := h.questionService.GetQuestionsByExam(c.Request.Context(), examID)
	if err != nil {
		InternalError(c, err.Error())
		return
	}

	Success(c, questions)
}

func (h *QuestionHandler) UpdateQuestion(c *gin.Context) {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		BadRequest(c, "invalid question id")
		return
	}

	var req models.QuestionUpdateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		ValidationError(c, err)
		return
	}

	question, err := h.questionService.UpdateQuestion(c.Request.Context(), id, &req)
	if err != nil {
		if err == services.ErrQuestionNotFound {
			NotFound(c, "question not found")
			return
		}
		if err == services.ErrExamCannotModify {
			Forbidden(c, "exam cannot be modified in current status")
			return
		}
		InternalError(c, err.Error())
		return
	}

	Success(c, question)
}

func (h *QuestionHandler) DeleteQuestion(c *gin.Context) {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		BadRequest(c, "invalid question id")
		return
	}

	if err := h.questionService.DeleteQuestion(c.Request.Context(), id); err != nil {
		if err == services.ErrQuestionNotFound {
			NotFound(c, "question not found")
			return
		}
		if err == services.ErrExamCannotModify {
			Forbidden(c, "exam cannot be modified in current status")
			return
		}
		InternalError(c, err.Error())
		return
	}

	NoContent(c)
}
