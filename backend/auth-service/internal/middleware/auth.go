package middleware

import (
	"net/http"
	"strings"

	"auth-service/pkg/jwt"

	"github.com/gin-gonic/gin"
)

func JWTAuth(jwtService *jwt.JWTService) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"code":    -1,
				"message": "missing authorization header",
			})
			c.Abort()
			return
		}

		parts := strings.SplitN(authHeader, " ", 2)
		if len(parts) != 2 || parts[0] != "Bearer" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"code":    -1,
				"message": "invalid authorization header format",
			})
			c.Abort()
			return
		}

		tokenString := parts[1]
		claims, err := jwtService.ValidateToken(tokenString)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{
				"code":    -1,
				"message": "invalid or expired token",
			})
			c.Abort()
			return
		}

		c.Set("user_id", claims.UserID)
		c.Set("username", claims.Username)
		c.Set("role_id", claims.RoleID)
		c.Set("role_code", claims.RoleCode)
		c.Set("permissions", claims.Permissions)
		c.Set("claims", claims)

		c.Next()
	}
}

func OptionalJWTAuth(jwtService *jwt.JWTService) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.Next()
			return
		}

		parts := strings.SplitN(authHeader, " ", 2)
		if len(parts) != 2 || parts[0] != "Bearer" {
			c.Next()
			return
		}

		tokenString := parts[1]
		claims, err := jwtService.ValidateToken(tokenString)
		if err != nil {
			c.Next()
			return
		}

		c.Set("user_id", claims.UserID)
		c.Set("username", claims.Username)
		c.Set("role_id", claims.RoleID)
		c.Set("role_code", claims.RoleCode)
		c.Set("permissions", claims.Permissions)
		c.Set("claims", claims)

		c.Next()
	}
}

func GetUserID(c *gin.Context) uint {
	if userID, exists := c.Get("user_id"); exists {
		return userID.(uint)
	}
	return 0
}

func GetUsername(c *gin.Context) string {
	if username, exists := c.Get("username"); exists {
		return username.(string)
	}
	return ""
}

func GetRoleCode(c *gin.Context) string {
	if roleCode, exists := c.Get("role_code"); exists {
		return roleCode.(string)
	}
	return ""
}

func GetPermissions(c *gin.Context) []string {
	if permissions, exists := c.Get("permissions"); exists {
		return permissions.([]string)
	}
	return nil
}
