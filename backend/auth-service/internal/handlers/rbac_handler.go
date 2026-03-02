package handlers

import (
	"net/http"
	"strconv"

	"auth-service/internal/models"
	"auth-service/internal/services"

	"github.com/gin-gonic/gin"
)

type RBACHandler struct {
	rbacService *services.RBACService
}

func NewRBACHandler(rbacService *services.RBACService) *RBACHandler {
	return &RBACHandler{
		rbacService: rbacService,
	}
}

func (h *RBACHandler) ListRoles(c *gin.Context) {
	roles, err := h.rbacService.GetAllRoles()
	if err != nil {
		Error(c, http.StatusInternalServerError, err.Error())
		return
	}

	Success(c, roles)
}

func (h *RBACHandler) GetRole(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		Error(c, http.StatusBadRequest, "invalid role id")
		return
	}

	role, err := h.rbacService.GetRoleByID(uint(id))
	if err != nil {
		Error(c, http.StatusNotFound, "role not found")
		return
	}

	Success(c, role)
}

func (h *RBACHandler) CreateRole(c *gin.Context) {
	var req struct {
		Name        string `json:"name" binding:"required"`
		Code        string `json:"code" binding:"required"`
		Description string `json:"description"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, err.Error())
		return
	}

	role := &models.Role{
		Name:        req.Name,
		Code:        req.Code,
		Description: req.Description,
	}

	if err := h.rbacService.CreateRole(role); err != nil {
		Error(c, http.StatusInternalServerError, err.Error())
		return
	}

	Success(c, role)
}

func (h *RBACHandler) UpdateRole(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		Error(c, http.StatusBadRequest, "invalid role id")
		return
	}

	var req struct {
		Name        string `json:"name"`
		Description string `json:"description"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, err.Error())
		return
	}

	role, err := h.rbacService.GetRoleByID(uint(id))
	if err != nil {
		Error(c, http.StatusNotFound, "role not found")
		return
	}

	if req.Name != "" {
		role.Name = req.Name
	}
	if req.Description != "" {
		role.Description = req.Description
	}

	if err := h.rbacService.UpdateRole(role); err != nil {
		Error(c, http.StatusInternalServerError, err.Error())
		return
	}

	Success(c, role)
}

func (h *RBACHandler) DeleteRole(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		Error(c, http.StatusBadRequest, "invalid role id")
		return
	}

	if err := h.rbacService.DeleteRole(uint(id)); err != nil {
		Error(c, http.StatusInternalServerError, err.Error())
		return
	}

	Success(c, nil)
}

func (h *RBACHandler) AssignPermissions(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		Error(c, http.StatusBadRequest, "invalid role id")
		return
	}

	var req struct {
		PermissionIDs []uint `json:"permission_ids" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, err.Error())
		return
	}

	if err := h.rbacService.AssignPermissions(uint(id), req.PermissionIDs); err != nil {
		Error(c, http.StatusInternalServerError, err.Error())
		return
	}

	Success(c, nil)
}

func (h *RBACHandler) ListPermissions(c *gin.Context) {
	permissions, err := h.rbacService.GetAllPermissions()
	if err != nil {
		Error(c, http.StatusInternalServerError, err.Error())
		return
	}

	Success(c, permissions)
}

func (h *RBACHandler) GetRolePermissions(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		Error(c, http.StatusBadRequest, "invalid role id")
		return
	}

	permissions, err := h.rbacService.GetPermissionsByRoleID(uint(id))
	if err != nil {
		Error(c, http.StatusNotFound, "role not found")
		return
	}

	Success(c, permissions)
}
