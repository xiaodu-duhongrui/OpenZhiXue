package middleware

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func RequireRoles(allowedRoles ...string) gin.HandlerFunc {
	return func(c *gin.Context) {
		roleCode := GetRoleCode(c)
		if roleCode == "" {
			c.JSON(http.StatusForbidden, gin.H{
				"code":    -1,
				"message": "no role information",
			})
			c.Abort()
			return
		}

		for _, role := range allowedRoles {
			if roleCode == role {
				c.Next()
				return
			}
		}

		c.JSON(http.StatusForbidden, gin.H{
			"code":    -1,
			"message": "insufficient role permissions",
		})
		c.Abort()
	}
}

func RequirePermissions(requiredPermissions ...string) gin.HandlerFunc {
	return func(c *gin.Context) {
		userPermissions := GetPermissions(c)
		if userPermissions == nil {
			c.JSON(http.StatusForbidden, gin.H{
				"code":    -1,
				"message": "no permission information",
			})
			c.Abort()
			return
		}

		permissionMap := make(map[string]bool)
		for _, perm := range userPermissions {
			permissionMap[perm] = true
		}

		for _, required := range requiredPermissions {
			if !permissionMap[required] {
				c.JSON(http.StatusForbidden, gin.H{
					"code":    -1,
					"message": "insufficient permissions",
				})
				c.Abort()
				return
			}
		}

		c.Next()
	}
}

func RequireAnyPermission(requiredPermissions ...string) gin.HandlerFunc {
	return func(c *gin.Context) {
		userPermissions := GetPermissions(c)
		if userPermissions == nil {
			c.JSON(http.StatusForbidden, gin.H{
				"code":    -1,
				"message": "no permission information",
			})
			c.Abort()
			return
		}

		permissionMap := make(map[string]bool)
		for _, perm := range userPermissions {
			permissionMap[perm] = true
		}

		for _, required := range requiredPermissions {
			if permissionMap[required] {
				c.Next()
				return
			}
		}

		c.JSON(http.StatusForbidden, gin.H{
			"code":    -1,
			"message": "insufficient permissions",
		})
		c.Abort()
	}
}

func RequireAdmin() gin.HandlerFunc {
	return RequireRoles("admin")
}

func RequireTeacher() gin.HandlerFunc {
	return RequireRoles("teacher", "admin")
}

func RequireUser() gin.HandlerFunc {
	return RequireRoles("student", "parent", "teacher", "admin")
}
