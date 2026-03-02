package models

import (
	"time"

	"github.com/google/uuid"
)

type SessionStatus string

const (
	SessionStatusNotStarted SessionStatus = "not_started"
	SessionStatusInProgress SessionStatus = "in_progress"
	SessionStatusSubmitted  SessionStatus = "submitted"
	SessionStatusGraded     SessionStatus = "graded"
	SessionStatusTimeout    SessionStatus = "timeout"
)

type ExamSession struct {
	ID           uuid.UUID    `json:"id" db:"id"`
	ExamID       uuid.UUID    `json:"examId" db:"exam_id"`
	StudentID    uuid.UUID    `json:"studentId" db:"student_id"`
	StartTime    time.Time    `json:"startTime" db:"start_time"`
	SubmitTime   *time.Time   `json:"submitTime" db:"submit_time"`
	EndTime      time.Time    `json:"endTime" db:"end_time"`
	Status       SessionStatus `json:"status" db:"status"`
	TotalScore   float64      `json:"totalScore" db:"total_score"`
	ElapsedTime  int          `json:"elapsedTime" db:"elapsed_time"`
	IPAddress    string       `json:"ipAddress" db:"ip_address"`
	UserAgent    string       `json:"userAgent" db:"user_agent"`
	CreatedAt    time.Time    `json:"createdAt" db:"created_at"`
	UpdatedAt    time.Time    `json:"updatedAt" db:"updated_at"`
}

func NewExamSession(examID, studentID uuid.UUID, duration int) *ExamSession {
	now := time.Now()
	return &ExamSession{
		ID:          uuid.New(),
		ExamID:      examID,
		StudentID:   studentID,
		StartTime:   now,
		EndTime:     now.Add(time.Duration(duration) * time.Minute),
		Status:      SessionStatusInProgress,
		CreatedAt:   now,
		UpdatedAt:   now,
	}
}

func (s *ExamSession) IsExpired() bool {
	return time.Now().After(s.EndTime)
}

func (s *ExamSession) RemainingTime() int {
	if s.IsExpired() {
		return 0
	}
	return int(time.Until(s.EndTime).Seconds())
}

type SessionStartRequest struct {
	IPAddress string `json:"ipAddress"`
	UserAgent string `json:"userAgent"`
}

type SessionSubmitRequest struct {
	Force bool `json:"force"`
}

type SessionResponse struct {
	ExamSession
	Exam         *Exam              `json:"exam,omitempty"`
	RemainingTime int               `json:"remainingTime"`
	Questions    []QuestionResponse `json:"questions,omitempty"`
}
