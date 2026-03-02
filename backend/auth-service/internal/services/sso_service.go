package services

import (
	"context"
	"errors"
	"time"

	"auth-service/internal/models"
	"auth-service/internal/repositories"
	"auth-service/pkg/jwt"
	"auth-service/pkg/oauth"
)

type SSOService struct {
	userRepo        *repositories.UserRepository
	roleRepo        *repositories.RoleRepository
	sessionRepo     *repositories.SessionRepository
	oauthAccountRepo *repositories.OAuthAccountRepository
	jwtService      *jwt.JWTService
	oauthService    *oauth.OAuthService
}

func NewSSOService(
	userRepo *repositories.UserRepository,
	roleRepo *repositories.RoleRepository,
	sessionRepo *repositories.SessionRepository,
	oauthAccountRepo *repositories.OAuthAccountRepository,
	jwtService *jwt.JWTService,
	oauthService *oauth.OAuthService,
) *SSOService {
	return &SSOService{
		userRepo:         userRepo,
		roleRepo:         roleRepo,
		sessionRepo:      sessionRepo,
		oauthAccountRepo: oauthAccountRepo,
		jwtService:       jwtService,
		oauthService:     oauthService,
	}
}

type SSOLoginResponse struct {
	Token *jwt.TokenPair `json:"token"`
	User  *models.User   `json:"user"`
	IsNew bool           `json:"is_new"`
}

func (s *SSOService) GetOAuthURL(provider, state string) string {
	return s.oauthService.GetAuthURL(provider, state)
}

func (s *SSOService) HandleWeChatCallback(ctx context.Context, code, ip, userAgent string) (*SSOLoginResponse, error) {
	oauthUserInfo, tokenResp, err := s.oauthService.HandleWeChatCallback(ctx, code)
	if err != nil {
		return nil, err
	}

	return s.handleOAuthLogin(ctx, oauthUserInfo, tokenResp.AccessToken, tokenResp.RefreshToken, ip, userAgent)
}

func (s *SSOService) HandleQQCallback(ctx context.Context, code, ip, userAgent string) (*SSOLoginResponse, error) {
	oauthUserInfo, tokenResp, err := s.oauthService.HandleQQCallback(ctx, code)
	if err != nil {
		return nil, err
	}

	return s.handleOAuthLogin(ctx, oauthUserInfo, tokenResp.AccessToken, tokenResp.RefreshToken, ip, userAgent)
}

func (s *SSOService) handleOAuthLogin(ctx context.Context, oauthUserInfo *oauth.OAuthUserInfo, accessToken, refreshToken, ip, userAgent string) (*SSOLoginResponse, error) {
	oauthAccount, err := s.oauthAccountRepo.FindByProviderAndID(oauthUserInfo.Provider, oauthUserInfo.ProviderID)
	isNew := false

	if err != nil {
		role, err := s.roleRepo.FindByCode("student")
		if err != nil {
			return nil, errors.New("default role not found")
		}

		user := &models.User{
			Username: oauthUserInfo.Provider + "_" + oauthUserInfo.ProviderID[:8],
			Email:    oauthUserInfo.Email,
			Nickname: oauthUserInfo.Nickname,
			Avatar:   oauthUserInfo.Avatar,
			RoleID:   role.ID,
			Status:   models.UserStatusActive,
		}

		if err := s.userRepo.Create(user); err != nil {
			return nil, err
		}

		user.Role = role

		expiresAt := time.Now().Add(time.Hour * 24 * 30)
		newOAuthAccount := &models.OAuthAccount{
			UserID:       user.ID,
			Provider:     oauthUserInfo.Provider,
			ProviderID:   oauthUserInfo.ProviderID,
			AccessToken:  accessToken,
			RefreshToken: refreshToken,
			ExpiresAt:    &expiresAt,
		}

		if err := s.oauthAccountRepo.Create(newOAuthAccount); err != nil {
			return nil, err
		}

		oauthAccount = newOAuthAccount
		isNew = true
	}

	user := oauthAccount.User
	if user == nil {
		user, err = s.userRepo.FindByID(oauthAccount.UserID)
		if err != nil {
			return nil, err
		}
	}

	if user.Status != models.UserStatusActive {
		return nil, errors.New("user account is not active")
	}

	var permissions []string
	if user.Role != nil {
		for _, perm := range user.Role.Permissions {
			permissions = append(permissions, perm.Code)
		}
	}

	tokenPair, err := s.jwtService.GenerateToken(user.ID, user.Username, user.RoleID, user.Role.Code, permissions)
	if err != nil {
		return nil, err
	}

	expiresAt := time.Now().Add(time.Duration(s.jwtService.RefreshTokenExpire()) * time.Second)
	session := &models.Session{
		UserID:       user.ID,
		Token:        tokenPair.AccessToken,
		RefreshToken: tokenPair.RefreshToken,
		IPAddress:    ip,
		UserAgent:    userAgent,
		ExpiresAt:    expiresAt,
	}

	if err := s.sessionRepo.Create(session); err != nil {
		return nil, err
	}

	if err := s.userRepo.UpdateLastLogin(user.ID, ip); err != nil {
		return nil, err
	}

	return &SSOLoginResponse{
		Token: tokenPair,
		User:  user,
		IsNew: isNew,
	}, nil
}

func (s *SSOService) LinkOAuthAccount(userID uint, provider, code string) error {
	var oauthUserInfo *oauth.OAuthUserInfo
	var accessToken, refreshToken string
	var err error

	ctx := context.Background()

	switch provider {
	case "wechat":
		oauthUserInfo, tokenResp, err := s.oauthService.HandleWeChatCallback(ctx, code)
		if err != nil {
			return err
		}
		accessToken = tokenResp.AccessToken
		refreshToken = tokenResp.RefreshToken
		return s.linkAccount(userID, oauthUserInfo, accessToken, refreshToken)
	case "qq":
		oauthUserInfo, tokenResp, err := s.oauthService.HandleQQCallback(ctx, code)
		if err != nil {
			return err
		}
		accessToken = tokenResp.AccessToken
		refreshToken = tokenResp.RefreshToken
		return s.linkAccount(userID, oauthUserInfo, accessToken, refreshToken)
	default:
		return errors.New("unsupported oauth provider")
	}
}

func (s *SSOService) linkAccount(userID uint, oauthUserInfo *oauth.OAuthUserInfo, accessToken, refreshToken string) error {
	existing, err := s.oauthAccountRepo.FindByProviderAndID(oauthUserInfo.Provider, oauthUserInfo.ProviderID)
	if err == nil && existing != nil {
		return errors.New("oauth account already linked to another user")
	}

	expiresAt := time.Now().Add(time.Hour * 24 * 30)
	oauthAccount := &models.OAuthAccount{
		UserID:       userID,
		Provider:     oauthUserInfo.Provider,
		ProviderID:   oauthUserInfo.ProviderID,
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		ExpiresAt:    &expiresAt,
	}

	return s.oauthAccountRepo.Create(oauthAccount)
}

func (s *SSOService) UnlinkOAuthAccount(userID uint, provider string) error {
	accounts, err := s.oauthAccountRepo.FindByUserID(userID)
	if err != nil {
		return err
	}

	for _, account := range accounts {
		if account.Provider == provider {
			return s.oauthAccountRepo.Delete(account.ID)
		}
	}

	return errors.New("oauth account not found")
}

func (s *SSOService) GetLinkedAccounts(userID uint) ([]models.OAuthAccount, error) {
	return s.oauthAccountRepo.FindByUserID(userID)
}

func (s *SSOService) GetActiveSessions(userID uint) ([]models.Session, error) {
	return s.sessionRepo.FindByUserID(userID)
}

func (s *SSOService) TerminateSession(sessionID uint) error {
	return s.sessionRepo.Delete(sessionID)
}

func (s *SSOService) TerminateAllSessions(userID uint) error {
	return s.sessionRepo.DeleteByUserID(userID)
}
