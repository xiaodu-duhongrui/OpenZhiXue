package models

import (
	"time"

	"github.com/google/uuid"
)

type ExamStatus string

const (
	ExamStatusDraft     ExamStatus = "draft"
	ExamStatusPublished ExamStatus = "published"
	ExamStatusOngoing   ExamStatus = "ongoing"
	ExamStatusEnded     ExamStatus = "ended"
	ExamStatusGraded    ExamStatus = "graded"
)

type ExamType string

const (
	ExamTypeQuiz       ExamType = "quiz"
	ExamTypeMidterm    ExamType = "midterm"
	ExamTypeFinal      ExamType = "final"
	ExamTypeMock       ExamType = "mock"
	ExamTypePractice   ExamType = "practice"
	ExamTypeAssignment ExamType = "assignment"
)

type Exam struct {
	ID          uuid.UUID  `json:"id" db:"id"`
	Name        string     `json:"name" db:"name"`
	Type        ExamType   `json:"type" db:"type"`
	SubjectIDs  []string   `json:"subjectIds" db:"subject_ids"`
	ClassIDs    []string   `json:"classIds" db:"class_ids"`
	StartTime   time.Time  `json:"startTime" db:"start_time"`
	EndTime     time.Time  `json:"endTime" db:"end_time"`
	Duration    int        `json:"duration" db:"duration"`
	Status      ExamStatus `json:"status" db:"status"`
	TotalScore  float64    `json:"totalScore" db:"total_score"`
	PassScore   float64    `json:"passScore" db:"pass_score"`
	Description string     `json:"description" db:"description"`
	CreatedBy   uuid.UUID  `json:"createdBy" db:"created_by"`
	CreatedAt   time.Time  `json:"createdAt" db:"created_at"`
	UpdatedAt   time.Time  `json:"updatedAt" db:"updated_at"`
}

func NewExam() *Exam {
	return &Exam{
		ID:        uuid.New(),
		Status:    ExamStatusDraft,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
}

type ExamCreateRequest struct {
	Name        string   `json:"name" binding:"required"`
	Type        ExamType `json:"type" binding:"required"`
	SubjectIDs  []string `json:"subjectIds" binding:"required"`
	ClassIDs    []string `json:"classIds" binding:"required"`
	StartTime   string   `json:"startTime" binding:"required"`
	EndTime     string   `json:"endTime" binding:"required"`
	Duration    int      `json:"duration" binding:"required,min=1"`
	TotalScore  float64  `json:"totalScore"`
	PassScore   float64  `json:"passScore"`
	Description string   `json:"description"`
}

type ExamUpdateRequest struct {
	Name        string   `json:"name"`
	Type        ExamType `json:"type"`
	SubjectIDs  []string `json:"subjectIds"`
	ClassIDs    []string `json:"classIds"`
	StartTime   string   `json:"startTime"`
	EndTime     string   `json:"endTime"`
	Duration    int      `json:"duration"`
	TotalScore  float64  `json:"totalScore"`
	PassScore   float64  `json:"passScore"`
	Description string   `json:"description"`
}

type ExamListResponse struct {
	Exams      []Exam `json:"exams"`
	Total      int64  `json:"total"`
	Page       int    `json:"page"`
	PageSize   int    `json:"pageSize"`
	TotalPages int    `json:"totalPages"`
}

type ExamFilter struct {
	Status    ExamStatus `form:"status"`
	Type      ExamType   `form:"type"`
	SubjectID string     `form:"subjectId"`
	ClassID   string     `form:"classId"`
	StartDate string     `form:"startDate"`
	EndDate   string     `form:"endDate"`
	Page      int        `form:"page" binding:"min=1"`
	PageSize  int        `form:"pageSize" binding:"min=1,max=100"`
}
