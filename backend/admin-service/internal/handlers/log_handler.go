package handlers

import (
	"net/http"

	"admin-service/internal/models"
	"admin-service/internal/repositories"

	"github.com/gin-gonic/gin"
)

type LogHandler struct {
	logRepo *repositories.LogRepository
}

func NewLogHandler(logRepo *repositories.LogRepository) *LogHandler {
	return &LogHandler{
		logRepo: logRepo,
	}
}

func (h *LogHandler) List(c *gin.Context) {
	var filter models.OperationLogFilter
	if err := c.ShouldBindQuery(&filter); err != nil {
		Error(c, http.StatusBadRequest, "invalid query parameters")
		return
	}

	logs, total, err := h.logRepo.List(&filter)
	if err != nil {
		Error(c, http.StatusInternalServerError, err.Error())
		return
	}

	Success(c, &models.OperationLogListResponse{
		Total: int(total),
		List:  logs,
	})
}

func (h *LogHandler) GetByID(c *gin.Context) {
	idStr := c.Param("id")
	id := 0
	if _, err := gin.H{"id": &id}; err != nil {
		Error(c, http.StatusBadRequest, "invalid log id")
		return
	}

	log, err := h.logRepo.FindByID(uint(id))
	if err != nil {
		Error(c, http.StatusNotFound, "log not found")
		return
	}

	Success(c, log)
}
