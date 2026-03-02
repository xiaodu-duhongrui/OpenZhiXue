package jwt

import (
	"errors"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

type Claims struct {
	UserID      uint   `json:"user_id"`
	Username    string `json:"username"`
	RoleID      uint   `json:"role_id"`
	RoleCode    string `json:"role_code"`
	Permissions []string `json:"permissions"`
	jwt.RegisteredClaims
}

type TokenPair struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
	ExpiresIn    int64  `json:"expires_in"`
	TokenType    string `json:"token_type"`
}

type JWTService struct {
	secret             string
	issuer             string
	accessTokenExpire  int
	refreshTokenExpire int
}

func NewJWTService(secret, issuer string, accessExpire, refreshExpire int) *JWTService {
	return &JWTService{
		secret:             secret,
		issuer:             issuer,
		accessTokenExpire:  accessExpire,
		refreshTokenExpire: refreshExpire,
	}
}

func (s *JWTService) GenerateToken(userID uint, username string, roleID uint, roleCode string, permissions []string) (*TokenPair, error) {
	now := time.Now()
	accessExpireAt := now.Add(time.Duration(s.accessTokenExpire) * time.Second)
	refreshExpireAt := now.Add(time.Duration(s.refreshTokenExpire) * time.Second)

	accessClaims := Claims{
		UserID:      userID,
		Username:    username,
		RoleID:      roleID,
		RoleCode:    roleCode,
		Permissions: permissions,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(accessExpireAt),
			IssuedAt:  jwt.NewNumericDate(now),
			NotBefore: jwt.NewNumericDate(now),
			Issuer:    s.issuer,
		},
	}

	accessToken := jwt.NewWithClaims(jwt.SigningMethodHS256, accessClaims)
	accessTokenString, err := accessToken.SignedString([]byte(s.secret))
	if err != nil {
		return nil, err
	}

	refreshClaims := Claims{
		UserID:   userID,
		Username: username,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(refreshExpireAt),
			IssuedAt:  jwt.NewNumericDate(now),
			NotBefore: jwt.NewNumericDate(now),
			Issuer:    s.issuer,
		},
	}

	refreshToken := jwt.NewWithClaims(jwt.SigningMethodHS256, refreshClaims)
	refreshTokenString, err := refreshToken.SignedString([]byte(s.secret))
	if err != nil {
		return nil, err
	}

	return &TokenPair{
		AccessToken:  accessTokenString,
		RefreshToken: refreshTokenString,
		ExpiresIn:    int64(s.accessTokenExpire),
		TokenType:    "Bearer",
	}, nil
}

func (s *JWTService) ParseToken(tokenString string) (*Claims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
		return []byte(s.secret), nil
	})

	if err != nil {
		return nil, err
	}

	if claims, ok := token.Claims.(*Claims); ok && token.Valid {
		return claims, nil
	}

	return nil, errors.New("invalid token")
}

func (s *JWTService) ValidateToken(tokenString string) (*Claims, error) {
	claims, err := s.ParseToken(tokenString)
	if err != nil {
		return nil, err
	}

	if claims.ExpiresAt != nil && claims.ExpiresAt.Before(time.Now()) {
		return nil, errors.New("token expired")
	}

	return claims, nil
}

func (s *JWTService) RefreshAccessToken(refreshTokenString string) (*TokenPair, error) {
	claims, err := s.ParseToken(refreshTokenString)
	if err != nil {
		return nil, err
	}

	if claims.ExpiresAt != nil && claims.ExpiresAt.Before(time.Now()) {
		return nil, errors.New("refresh token expired")
	}

	return s.GenerateToken(claims.UserID, claims.Username, claims.RoleID, claims.RoleCode, claims.Permissions)
}
