package integration

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

type LoginRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

type LoginResponse struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
	Data    struct {
		Token struct {
			AccessToken  string `json:"access_token"`
			RefreshToken string `json:"refresh_token"`
		} `json:"token"`
		User struct {
			ID       uint   `json:"id"`
			Username string `json:"username"`
			Email    string `json:"email"`
		} `json:"user"`
	} `json:"data"`
}

type APIResponse struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    interface{} `json:"data"`
}

func TestAPIIntegration_LoginFlow(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	router := gin.New()
	
	router.POST("/api/auth/login", func(c *gin.Context) {
		var req LoginRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, APIResponse{Code: -1, Message: "invalid request"})
			return
		}
		
		if req.Username == "testuser" && req.Password == "password123" {
			c.JSON(http.StatusOK, APIResponse{
				Code:    0,
				Message: "success",
				Data: gin.H{
					"token": gin.H{
						"access_token":  "test-access-token",
						"refresh_token": "test-refresh-token",
					},
					"user": gin.H{
						"id":       1,
						"username": "testuser",
						"email":    "test@example.com",
					},
				},
			})
			return
		}
		
		c.JSON(http.StatusUnauthorized, APIResponse{Code: -1, Message: "invalid credentials"})
	})
	
	t.Run("successful login", func(t *testing.T) {
		reqBody := LoginRequest{Username: "testuser", Password: "password123"}
		body, _ := json.Marshal(reqBody)
		
		w := httptest.NewRecorder()
		req := httptest.NewRequest(http.MethodPost, "/api/auth/login", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")
		
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response APIResponse
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.Equal(t, 0, response.Code)
	})
	
	t.Run("invalid credentials", func(t *testing.T) {
		reqBody := LoginRequest{Username: "wronguser", Password: "wrongpass"}
		body, _ := json.Marshal(reqBody)
		
		w := httptest.NewRecorder()
		req := httptest.NewRequest(http.MethodPost, "/api/auth/login", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")
		
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestAPIIntegration_ProtectedRoute(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	router := gin.New()
	
	router.Use(func(c *gin.Context) {
		token := c.GetHeader("Authorization")
		if token == "" {
			c.JSON(http.StatusUnauthorized, APIResponse{Code: -1, Message: "unauthorized"})
			c.Abort()
			return
		}
		c.Set("user_id", uint(1))
		c.Next()
	})
	
	router.GET("/api/profile", func(c *gin.Context) {
		userID, _ := c.Get("user_id")
		c.JSON(http.StatusOK, APIResponse{
			Code:    0,
			Message: "success",
			Data: gin.H{
				"id":       userID,
				"username": "testuser",
			},
		})
	})
	
	t.Run("with valid token", func(t *testing.T) {
		w := httptest.NewRecorder()
		req := httptest.NewRequest(http.MethodGet, "/api/profile", nil)
		req.Header.Set("Authorization", "Bearer test-token")
		
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
	})
	
	t.Run("without token", func(t *testing.T) {
		w := httptest.NewRecorder()
		req := httptest.NewRequest(http.MethodGet, "/api/profile", nil)
		
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestAPIIntegration_ExamWorkflow(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	router := gin.New()
	
	exams := make(map[string]interface{})
	
	router.POST("/api/exams", func(c *gin.Context) {
		var req map[string]interface{}
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, APIResponse{Code: -1, Message: "invalid request"})
			return
		}
		
		req["id"] = "exam-123"
		req["status"] = "draft"
		exams["exam-123"] = req
		
		c.JSON(http.StatusCreated, APIResponse{
			Code:    0,
			Message: "success",
			Data:    req,
		})
	})
	
	router.GET("/api/exams/:id", func(c *gin.Context) {
		id := c.Param("id")
		exam, exists := exams[id]
		if !exists {
			c.JSON(http.StatusNotFound, APIResponse{Code: -1, Message: "exam not found"})
			return
		}
		
		c.JSON(http.StatusOK, APIResponse{
			Code:    0,
			Message: "success",
			Data:    exam,
		})
	})
	
	router.POST("/api/exams/:id/publish", func(c *gin.Context) {
		id := c.Param("id")
		exam, exists := exams[id]
		if !exists {
			c.JSON(http.StatusNotFound, APIResponse{Code: -1, Message: "exam not found"})
			return
		}
		
		examMap := exam.(map[string]interface{})
		examMap["status"] = "published"
		exams[id] = examMap
		
		c.JSON(http.StatusOK, APIResponse{
			Code:    0,
			Message: "success",
			Data:    examMap,
		})
	})
	
	t.Run("create exam", func(t *testing.T) {
		reqBody := map[string]interface{}{
			"name":      "Midterm Exam",
			"type":      "midterm",
			"duration":  120,
			"total_score": 100,
		}
		body, _ := json.Marshal(reqBody)
		
		w := httptest.NewRecorder()
		req := httptest.NewRequest(http.MethodPost, "/api/exams", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")
		
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusCreated, w.Code)
		
		var response APIResponse
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.Equal(t, 0, response.Code)
	})
	
	t.Run("get exam", func(t *testing.T) {
		w := httptest.NewRecorder()
		req := httptest.NewRequest(http.MethodGet, "/api/exams/exam-123", nil)
		
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
	})
	
	t.Run("publish exam", func(t *testing.T) {
		w := httptest.NewRecorder()
		req := httptest.NewRequest(http.MethodPost, "/api/exams/exam-123/publish", nil)
		
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response APIResponse
		json.Unmarshal(w.Body.Bytes(), &response)
		data := response.Data.(map[string]interface{})
		assert.Equal(t, "published", data["status"])
	})
}

func TestAPIIntegration_RateLimiting(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	router := gin.New()
	
	requestCount := 0
	maxRequests := 5
	
	router.Use(func(c *gin.Context) {
		requestCount++
		if requestCount > maxRequests {
			c.JSON(http.StatusTooManyRequests, APIResponse{
				Code:    -1,
				Message: "rate limit exceeded",
			})
			c.Abort()
			return
		}
		c.Next()
	})
	
	router.GET("/api/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, APIResponse{Code: 0, Message: "success"})
	})
	
	for i := 0; i < maxRequests; i++ {
		w := httptest.NewRecorder()
		req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
		router.ServeHTTP(w, req)
		assert.Equal(t, http.StatusOK, w.Code)
	}
	
	w := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
	router.ServeHTTP(w, req)
	assert.Equal(t, http.StatusTooManyRequests, w.Code)
}

func TestAPIIntegration_Timeout(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	router := gin.New()
	
	router.GET("/api/slow", func(c *gin.Context) {
		time.Sleep(2 * time.Second)
		c.JSON(http.StatusOK, APIResponse{Code: 0, Message: "success"})
	})
	
	w := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodGet, "/api/slow", nil)
	
	done := make(chan bool)
	go func() {
		router.ServeHTTP(w, req)
		done <- true
	}()
	
	select {
	case <-done:
		assert.Equal(t, http.StatusOK, w.Code)
	case <-time.After(3 * time.Second):
		t.Error("Request timed out")
	}
}
