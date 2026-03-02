package handlers

import (
	"net/http"

	"admin-service/internal/repositories"
	"admin-service/internal/services"

	"github.com/gin-gonic/gin"
)

type ImportHandler struct {
	importService *services.ImportService
	logRepo       *repositories.LogRepository
}

func NewImportHandler(importService *services.ImportService, logRepo *repositories.LogRepository) *ImportHandler {
	return &ImportHandler{
		importService: importService,
		logRepo:       logRepo,
	}
}

func (h *ImportHandler) Upload(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		Error(c, http.StatusBadRequest, "file is required")
		return
	}

	data, err := file.Open()
	if err != nil {
		Error(c, http.StatusInternalServerError, "failed to open file")
		return
	}
	defer data.Close()

	fileData := make([]byte, file.Size)
	_, err = data.Read(fileData)
	if err != nil {
		Error(c, http.StatusInternalServerError, "failed to read file")
		return
	}

	result, err := h.importService.Upload(fileData, file.Filename)
	if err != nil {
		Error(c, http.StatusBadRequest, err.Error())
		return
	}

	Success(c, result)
}

func (h *ImportHandler) Preview(c *gin.Context) {
	var req struct {
		ImportID string `json:"import_id" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, "import_id is required")
		return
	}

	result, err := h.importService.Preview(req.ImportID)
	if err != nil {
		Error(c, http.StatusBadRequest, err.Error())
		return
	}

	Success(c, result)
}

func (h *ImportHandler) Confirm(c *gin.Context) {
	var req struct {
		ImportID string `json:"import_id" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, "import_id is required")
		return
	}

	adminID, _ := c.Get("admin_id")
	adminName, _ := c.Get("username")

	result, err := h.importService.Confirm(req.ImportID, adminID.(uint), adminName.(string), c.ClientIP())
	if err != nil {
		Error(c, http.StatusBadRequest, err.Error())
		return
	}

	Success(c, result)
}

func (h *ImportHandler) DownloadTemplate(c *gin.Context) {
	data, err := h.importService.GetTemplate()
	if err != nil {
		Error(c, http.StatusInternalServerError, "failed to generate template")
		return
	}

	c.Header("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
	c.Header("Content-Disposition", "attachment; filename=user_import_template.xlsx")
	c.Data(http.StatusOK, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", data)
}
