package handlers

import (
	"encoding/json"
	"net/http"
	"strconv"

	"admin-service/internal/models"
	"admin-service/internal/repositories"
	"admin-service/internal/services"

	"github.com/gin-gonic/gin"
)

type UserHandler struct {
	userService *services.UserService
	userRepo    *repositories.UserRepository
	logRepo     *repositories.LogRepository
}

func NewUserHandler(userService *services.UserService, userRepo *repositories.UserRepository, logRepo *repositories.LogRepository) *UserHandler {
	return &UserHandler{
		userService: userService,
		userRepo:    userRepo,
		logRepo:     logRepo,
	}
}

func (h *UserHandler) List(c *gin.Context) {
	var filter models.UserFilter
	if err := c.ShouldBindQuery(&filter); err != nil {
		Error(c, http.StatusBadRequest, "invalid query parameters")
		return
	}

	result, err := h.userService.List(&filter)
	if err != nil {
		Error(c, http.StatusInternalServerError, err.Error())
		return
	}

	Success(c, result)
}

func (h *UserHandler) GetByID(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		Error(c, http.StatusBadRequest, "invalid user id")
		return
	}

	user, err := h.userService.GetByID(uint(id))
	if err != nil {
		Error(c, http.StatusNotFound, err.Error())
		return
	}

	Success(c, user)
}

func (h *UserHandler) Create(c *gin.Context) {
	var req services.CreateUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, "invalid request parameters")
		return
	}

	user, err := h.userService.Create(&req)
	if err != nil {
		Error(c, http.StatusBadRequest, err.Error())
		return
	}

	h.logOperation(c, "create_user", "user", user.ID, map[string]interface{}{
		"username": user.Username,
		"real_name": user.RealName,
		"role":      user.Role,
	})

	Success(c, user)
}

func (h *UserHandler) Update(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		Error(c, http.StatusBadRequest, "invalid user id")
		return
	}

	var req services.UpdateUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, "invalid request parameters")
		return
	}

	user, err := h.userService.Update(uint(id), &req)
	if err != nil {
		Error(c, http.StatusBadRequest, err.Error())
		return
	}

	h.logOperation(c, "update_user", "user", user.ID, map[string]interface{}{
		"username": user.Username,
		"updates":  req,
	})

	Success(c, user)
}

func (h *UserHandler) Delete(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		Error(c, http.StatusBadRequest, "invalid user id")
		return
	}

	user, _ := h.userService.GetByID(uint(id))

	if err := h.userService.Delete(uint(id)); err != nil {
		Error(c, http.StatusBadRequest, err.Error())
		return
	}

	if user != nil {
		h.logOperation(c, "delete_user", "user", uint(id), map[string]interface{}{
			"username": user.Username,
		})
	}

	Success(c, gin.H{"message": "user deleted successfully"})
}

func (h *UserHandler) ChangePassword(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		Error(c, http.StatusBadRequest, "invalid user id")
		return
	}

	var req services.ChangePasswordRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, "invalid request parameters")
		return
	}

	if err := h.userService.ChangePassword(uint(id), req.NewPassword); err != nil {
		Error(c, http.StatusBadRequest, err.Error())
		return
	}

	h.logOperation(c, "change_user_password", "user", uint(id), nil)

	Success(c, gin.H{"message": "password changed successfully"})
}

func (h *UserHandler) logOperation(c *gin.Context, action, module string, targetID uint, detail map[string]interface{}) {
	adminID, _ := c.Get("admin_id")
	adminName, _ := c.Get("username")

	detailJSON, _ := json.Marshal(detail)

	log := &models.OperationLog{
		AdminID:    adminID.(uint),
		AdminName:  adminName.(string),
		Action:     action,
		Module:     module,
		TargetType: "user",
		TargetID:   targetID,
		Detail:     string(detailJSON),
		IP:         c.ClientIP(),
		UserAgent:  c.GetHeader("User-Agent"),
	}

	h.logRepo.Create(log)
}
