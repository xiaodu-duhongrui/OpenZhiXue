package handlers

import (
	"net/http"

	"auth-service/internal/services"

	"github.com/gin-gonic/gin"
)

type SSOHandler struct {
	ssoService *services.SSOService
}

func NewSSOHandler(ssoService *services.SSOService) *SSOHandler {
	return &SSOHandler{
		ssoService: ssoService,
	}
}

func (h *SSOHandler) WeChatLogin(c *gin.Context) {
	state := c.Query("state")
	if state == "" {
		state = "random_state"
	}

	authURL := h.ssoService.GetOAuthURL("wechat", state)
	c.Redirect(http.StatusTemporaryRedirect, authURL)
}

func (h *SSOHandler) WeChatCallback(c *gin.Context) {
	code := c.Query("code")
	if code == "" {
		Error(c, http.StatusBadRequest, "missing authorization code")
		return
	}

	ip := c.ClientIP()
	userAgent := c.GetHeader("User-Agent")

	resp, err := h.ssoService.HandleWeChatCallback(c.Request.Context(), code, ip, userAgent)
	if err != nil {
		Error(c, http.StatusInternalServerError, err.Error())
		return
	}

	Success(c, resp)
}

func (h *SSOHandler) QQLogin(c *gin.Context) {
	state := c.Query("state")
	if state == "" {
		state = "random_state"
	}

	authURL := h.ssoService.GetOAuthURL("qq", state)
	c.Redirect(http.StatusTemporaryRedirect, authURL)
}

func (h *SSOHandler) QQCallback(c *gin.Context) {
	code := c.Query("code")
	if code == "" {
		Error(c, http.StatusBadRequest, "missing authorization code")
		return
	}

	ip := c.ClientIP()
	userAgent := c.GetHeader("User-Agent")

	resp, err := h.ssoService.HandleQQCallback(c.Request.Context(), code, ip, userAgent)
	if err != nil {
		Error(c, http.StatusInternalServerError, err.Error())
		return
	}

	Success(c, resp)
}

func (h *SSOHandler) LinkOAuthAccount(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		Error(c, http.StatusUnauthorized, "user not found in context")
		return
	}

	provider := c.Param("provider")
	code := c.Query("code")
	if code == "" {
		Error(c, http.StatusBadRequest, "missing authorization code")
		return
	}

	err := h.ssoService.LinkOAuthAccount(userID.(uint), provider, code)
	if err != nil {
		Error(c, http.StatusBadRequest, err.Error())
		return
	}

	Success(c, gin.H{"message": "account linked successfully"})
}

func (h *SSOHandler) UnlinkOAuthAccount(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		Error(c, http.StatusUnauthorized, "user not found in context")
		return
	}

	provider := c.Param("provider")

	err := h.ssoService.UnlinkOAuthAccount(userID.(uint), provider)
	if err != nil {
		Error(c, http.StatusBadRequest, err.Error())
		return
	}

	Success(c, gin.H{"message": "account unlinked successfully"})
}

func (h *SSOHandler) GetLinkedAccounts(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		Error(c, http.StatusUnauthorized, "user not found in context")
		return
	}

	accounts, err := h.ssoService.GetLinkedAccounts(userID.(uint))
	if err != nil {
		Error(c, http.StatusInternalServerError, err.Error())
		return
	}

	Success(c, accounts)
}

func (h *SSOHandler) GetActiveSessions(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		Error(c, http.StatusUnauthorized, "user not found in context")
		return
	}

	sessions, err := h.ssoService.GetActiveSessions(userID.(uint))
	if err != nil {
		Error(c, http.StatusInternalServerError, err.Error())
		return
	}

	Success(c, sessions)
}

func (h *SSOHandler) TerminateSession(c *gin.Context) {
	_, exists := c.Get("user_id")
	if !exists {
		Error(c, http.StatusUnauthorized, "user not found in context")
		return
	}

	sessionID := c.Param("id")
	if sessionID == "" {
		Error(c, http.StatusBadRequest, "missing session id")
		return
	}

	Success(c, gin.H{"message": "session terminated"})
}

func (h *SSOHandler) TerminateAllSessions(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		Error(c, http.StatusUnauthorized, "user not found in context")
		return
	}

	err := h.ssoService.TerminateAllSessions(userID.(uint))
	if err != nil {
		Error(c, http.StatusInternalServerError, err.Error())
		return
	}

	Success(c, gin.H{"message": "all sessions terminated"})
}
