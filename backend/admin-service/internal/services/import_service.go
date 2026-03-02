package services

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"admin-service/internal/models"
	"admin-service/internal/repositories"
	"admin-service/pkg/xlsx"

	"github.com/google/uuid"
)

var (
	ErrFileTooLarge   = errors.New("file too large")
	ErrInvalidFile    = errors.New("invalid file format")
	ErrImportNotFound = errors.New("import record not found")
)

type ImportService struct {
	userRepo   *repositories.UserRepository
	logRepo    *repositories.LogRepository
	uploadDir  string
	maxSize    int64
	imports    map[string]*ImportSession
}

type ImportSession struct {
	ID        string
	FilePath  string
	Data      []*xlsx.UserImportData
	CreatedAt time.Time
	Status    string
}

func NewImportService(userRepo *repositories.UserRepository, logRepo *repositories.LogRepository, uploadDir string, maxSize int64) *ImportService {
	os.MkdirAll(uploadDir, 0755)
	return &ImportService{
		userRepo:   userRepo,
		logRepo:    logRepo,
		uploadDir:  uploadDir,
		maxSize:    maxSize,
		imports:    make(map[string]*ImportSession),
	}
}

type UploadResponse struct {
	ImportID  string `json:"import_id"`
	FileName  string `json:"file_name"`
	Size      int64  `json:"size"`
	SheetName string `json:"sheet_name"`
}

type PreviewResponse struct {
	ImportID string                 `json:"import_id"`
	Total    int                    `json:"total"`
	Valid    int                    `json:"valid"`
	Invalid  int                    `json:"invalid"`
	Data     []*xlsx.UserImportData `json:"data"`
}

type ImportResult struct {
	ImportID string `json:"import_id"`
	Total    int    `json:"total"`
	Success  int    `json:"success"`
	Failed   int    `json:"failed"`
}

func (s *ImportService) Upload(data []byte, filename string) (*UploadResponse, error) {
	if int64(len(data)) > s.maxSize {
		return nil, ErrFileTooLarge
	}

	ext := filepath.Ext(filename)
	if ext != ".xlsx" && ext != ".xls" {
		return nil, ErrInvalidFile
	}

	importID := uuid.New().String()
	filePath := filepath.Join(s.uploadDir, importID+ext)

	if err := os.WriteFile(filePath, data, 0644); err != nil {
		return nil, err
	}

	parser := xlsx.NewParser()
	if err := parser.OpenFile(filePath); err != nil {
		os.Remove(filePath)
		return nil, err
	}
	defer parser.Close()

	sheetName := parser.GetSheetNames()[0]

	s.imports[importID] = &ImportSession{
		ID:        importID,
		FilePath:  filePath,
		CreatedAt: time.Now(),
		Status:    "uploaded",
	}

	return &UploadResponse{
		ImportID:  importID,
		FileName:  filename,
		Size:      int64(len(data)),
		SheetName: sheetName,
	}, nil
}

func (s *ImportService) Preview(importID string) (*PreviewResponse, error) {
	session, ok := s.imports[importID]
	if !ok {
		return nil, ErrImportNotFound
	}

	parser := xlsx.NewParser()
	if err := parser.OpenFile(session.FilePath); err != nil {
		return nil, err
	}
	defer parser.Close()

	data, err := parser.ParseUsers(parser.GetSheetNames()[0])
	if err != nil {
		return nil, err
	}

	session.Data = data
	session.Status = "previewed"

	valid := 0
	invalid := 0
	for _, d := range data {
		if d.Errors == "" {
			valid++
		} else {
			invalid++
		}
	}

	return &PreviewResponse{
		ImportID: importID,
		Total:    len(data),
		Valid:    valid,
		Invalid:  invalid,
		Data:     data,
	}, nil
}

func (s *ImportService) Confirm(importID string, adminID uint, adminName, ip string) (*ImportResult, error) {
	session, ok := s.imports[importID]
	if !ok {
		return nil, ErrImportNotFound
	}

	if session.Data == nil {
		return nil, errors.New("please preview first")
	}

	result := &ImportResult{
		ImportID: importID,
		Total:    len(session.Data),
	}

	var users []*models.User
	var failedItems []map[string]interface{}

	for _, d := range session.Data {
		if d.Errors != "" {
			result.Failed++
			failedItems = append(failedItems, map[string]interface{}{
				"row":     d.Row,
				"error":   d.Errors,
				"username": d.Username,
			})
			continue
		}

		user := &models.User{
			Username: d.Username,
			Password: d.Password,
			RealName: d.RealName,
			Role:     d.Role,
			Email:    d.Email,
			Phone:    d.Phone,
			ClassID:  &d.ClassID,
			Status:   1,
		}
		users = append(users, user)
	}

	if len(users) > 0 {
		if err := s.userRepo.CreateBatch(users); err != nil {
			return nil, err
		}
		result.Success = len(users)
	}

	detailJSON, _ := json.Marshal(map[string]interface{}{
		"total":   result.Total,
		"success": result.Success,
		"failed":  result.Failed,
		"items":   failedItems,
	})

	log := &models.OperationLog{
		AdminID:    adminID,
		AdminName:  adminName,
		Action:     "import_users",
		Module:     "user",
		TargetType: "batch",
		Detail:     string(detailJSON),
		IP:         ip,
	}
	s.logRepo.Create(log)

	delete(s.imports, importID)
	os.Remove(session.FilePath)

	return result, nil
}

func (s *ImportService) GetTemplate() ([]byte, error) {
	return xlsx.GenerateTemplate()
}

func (s *ImportService) Cleanup() {
	now := time.Now()
	for id, session := range s.imports {
		if now.Sub(session.CreatedAt) > 30*time.Minute {
			os.Remove(session.FilePath)
			delete(s.imports, id)
		}
	}
}

func (s *ImportService) GetImportStatus(importID string) (*ImportSession, error) {
	session, ok := s.imports[importID]
	if !ok {
		return nil, ErrImportNotFound
	}
	return session, nil
}
