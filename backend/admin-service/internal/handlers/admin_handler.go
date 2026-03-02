package handlers

import (
	"net/http"

	"admin-service/internal/services"
	"admin-service/pkg/jwt"

	"github.com/gin-gonic/gin"
)

type AdminHandler struct {
	adminService *services.AdminService
	jwtService   *jwt.JWTService
}

func NewAdminHandler(adminService *services.AdminService, jwtService *jwt.JWTService) *AdminHandler {
	return &AdminHandler{
		adminService: adminService,
		jwtService:   jwtService,
	}
}

type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

func (h *AdminHandler) Login(c *gin.Context) {
	var req LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, "invalid request parameters")
		return
	}

	resp, err := h.adminService.Login(&services.LoginRequest{
		Username: req.Username,
		Password: req.Password,
	})
	if err != nil {
		Error(c, http.StatusUnauthorized, err.Error())
		return
	}

	Success(c, resp)
}

func (h *AdminHandler) GetProfile(c *gin.Context) {
	adminID, exists := c.Get("admin_id")
	if !exists {
		Error(c, http.StatusUnauthorized, "unauthorized")
		return
	}

	info, err := h.adminService.GetAdminInfo(adminID.(uint))
	if err != nil {
		Error(c, http.StatusNotFound, err.Error())
		return
	}

	Success(c, info)
}

type ChangePasswordRequest struct {
	OldPassword string `json:"old_password" binding:"required"`
	NewPassword string `json:"new_password" binding:"required,min=6"`
}

func (h *AdminHandler) ChangePassword(c *gin.Context) {
	adminID, exists := c.Get("admin_id")
	if !exists {
		Error(c, http.StatusUnauthorized, "unauthorized")
		return
	}

	var req ChangePasswordRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, "invalid request parameters")
		return
	}

	err := h.adminService.ChangePassword(adminID.(uint), req.OldPassword, req.NewPassword)
	if err != nil {
		Error(c, http.StatusBadRequest, err.Error())
		return
	}

	Success(c, gin.H{"message": "password changed successfully"})
}
