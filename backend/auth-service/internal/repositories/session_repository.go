package repositories

import (
	"auth-service/internal/database"
	"auth-service/internal/models"
	"time"

	"gorm.io/gorm"
)

type SessionRepository struct {
	db *gorm.DB
}

func NewSessionRepository() *SessionRepository {
	return &SessionRepository{db: database.GetDB()}
}

func (r *SessionRepository) Create(session *models.Session) error {
	return r.db.Create(session).Error
}

func (r *SessionRepository) Update(session *models.Session) error {
	return r.db.Save(session).Error
}

func (r *SessionRepository) Delete(id uint) error {
	return r.db.Delete(&models.Session{}, id).Error
}

func (r *SessionRepository) FindByToken(token string) (*models.Session, error) {
	var session models.Session
	err := r.db.Preload("User.Role.Permissions").Where("token = ?", token).First(&session).Error
	if err != nil {
		return nil, err
	}
	return &session, nil
}

func (r *SessionRepository) FindByRefreshToken(refreshToken string) (*models.Session, error) {
	var session models.Session
	err := r.db.Preload("User.Role.Permissions").Where("refresh_token = ?", refreshToken).First(&session).Error
	if err != nil {
		return nil, err
	}
	return &session, nil
}

func (r *SessionRepository) FindByUserID(userID uint) ([]models.Session, error) {
	var sessions []models.Session
	err := r.db.Where("user_id = ?", userID).Find(&sessions).Error
	return sessions, err
}

func (r *SessionRepository) DeleteByToken(token string) error {
	return r.db.Where("token = ?", token).Delete(&models.Session{}).Error
}

func (r *SessionRepository) DeleteByUserID(userID uint) error {
	return r.db.Where("user_id = ?", userID).Delete(&models.Session{}).Error
}

func (r *SessionRepository) DeleteExpired() error {
	return r.db.Where("expires_at < ?", time.Now()).Delete(&models.Session{}).Error
}

func (r *SessionRepository) CleanupExpired() error {
	return r.db.Where("expires_at < ?", time.Now()).Delete(&models.Session{}).Error
}

type OAuthAccountRepository struct {
	db *gorm.DB
}

func NewOAuthAccountRepository() *OAuthAccountRepository {
	return &OAuthAccountRepository{db: database.GetDB()}
}

func (r *OAuthAccountRepository) Create(account *models.OAuthAccount) error {
	return r.db.Create(account).Error
}

func (r *OAuthAccountRepository) Update(account *models.OAuthAccount) error {
	return r.db.Save(account).Error
}

func (r *OAuthAccountRepository) FindByProviderAndID(provider, providerID string) (*models.OAuthAccount, error) {
	var account models.OAuthAccount
	err := r.db.Preload("User.Role.Permissions").Where("provider = ? AND provider_id = ?", provider, providerID).First(&account).Error
	if err != nil {
		return nil, err
	}
	return &account, nil
}

func (r *OAuthAccountRepository) FindByUserID(userID uint) ([]models.OAuthAccount, error) {
	var accounts []models.OAuthAccount
	err := r.db.Where("user_id = ?", userID).Find(&accounts).Error
	return accounts, err
}

func (r *OAuthAccountRepository) Delete(id uint) error {
	return r.db.Delete(&models.OAuthAccount{}, id).Error
}
