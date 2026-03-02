package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/openzhixue/exam-service/internal/services"
)

type StatisticsHandler struct {
	statisticsService *services.StatisticsService
}

func NewStatisticsHandler(statisticsService *services.StatisticsService) *StatisticsHandler {
	return &StatisticsHandler{
		statisticsService: statisticsService,
	}
}

func (h *StatisticsHandler) GetExamStatistics(c *gin.Context) {
	examIDStr := c.Param("id")
	examID, err := uuid.Parse(examIDStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	stats, err := h.statisticsService.GetExamStatistics(c.Request.Context(), examID)
	if err != nil {
		NotFound(c, "exam not found")
		return
	}

	Success(c, stats)
}

func (h *StatisticsHandler) GetExamAnalysis(c *gin.Context) {
	examIDStr := c.Param("id")
	examID, err := uuid.Parse(examIDStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	analysis, err := h.statisticsService.GetExamAnalysis(c.Request.Context(), examID)
	if err != nil {
		NotFound(c, "exam not found")
		return
	}

	Success(c, analysis)
}

func (h *StatisticsHandler) GetQuestionStatistics(c *gin.Context) {
	examIDStr := c.Param("id")
	examID, err := uuid.Parse(examIDStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	stats, err := h.statisticsService.GetQuestionStatistics(c.Request.Context(), examID)
	if err != nil {
		InternalError(c, err.Error())
		return
	}

	Success(c, stats)
}

func (h *StatisticsHandler) GetScoreDistribution(c *gin.Context) {
	examIDStr := c.Param("id")
	examID, err := uuid.Parse(examIDStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	distribution, err := h.statisticsService.GetScoreDistribution(c.Request.Context(), examID)
	if err != nil {
		InternalError(c, err.Error())
		return
	}

	Success(c, distribution)
}

func (h *StatisticsHandler) GetRanking(c *gin.Context) {
	examIDStr := c.Param("id")
	examID, err := uuid.Parse(examIDStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("pageSize", "20"))

	if page < 1 {
		page = 1
	}
	if pageSize < 1 || pageSize > 100 {
		pageSize = 20
	}

	ranking, err := h.statisticsService.GetRanking(c.Request.Context(), examID, page, pageSize)
	if err != nil {
		InternalError(c, err.Error())
		return
	}

	Success(c, ranking)
}

func (h *StatisticsHandler) GetTopPerformers(c *gin.Context) {
	examIDStr := c.Param("id")
	examID, err := uuid.Parse(examIDStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "10"))
	if limit < 1 || limit > 100 {
		limit = 10
	}

	performers, err := h.statisticsService.GetTopPerformers(c.Request.Context(), examID, limit)
	if err != nil {
		InternalError(c, err.Error())
		return
	}

	Success(c, performers)
}

func (h *StatisticsHandler) GetBottomPerformers(c *gin.Context) {
	examIDStr := c.Param("id")
	examID, err := uuid.Parse(examIDStr)
	if err != nil {
		BadRequest(c, "invalid exam id")
		return
	}

	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "10"))
	if limit < 1 || limit > 100 {
		limit = 10
	}

	performers, err := h.statisticsService.GetBottomPerformers(c.Request.Context(), examID, limit)
	if err != nil {
		InternalError(c, err.Error())
		return
	}

	Success(c, performers)
}
