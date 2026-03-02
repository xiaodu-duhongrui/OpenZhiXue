package models

import (
	"time"

	"github.com/google/uuid"
)

type AnswerStatus string

const (
	AnswerStatusPending  AnswerStatus = "pending"
	AnswerStatusCorrect  AnswerStatus = "correct"
	AnswerStatusWrong    AnswerStatus = "wrong"
	AnswerStatusPartial  AnswerStatus = "partial"
	AnswerStatusGraded   AnswerStatus = "graded"
)

type ExamAnswer struct {
	ID           uuid.UUID    `json:"id" db:"id"`
	SessionID    uuid.UUID    `json:"sessionId" db:"session_id"`
	QuestionID   uuid.UUID    `json:"questionId" db:"question_id"`
	Answer       string       `json:"answer" db:"answer"`
	Score        float64      `json:"score" db:"score"`
	MaxScore     float64      `json:"maxScore" db:"max_score"`
	Status       AnswerStatus `json:"status" db:"status"`
	GradedBy     *uuid.UUID   `json:"gradedBy" db:"graded_by"`
	GradedAt     *time.Time   `json:"gradedAt" db:"graded_at"`
	Feedback     string       `json:"feedback" db:"feedback"`
	AutoGraded   bool         `json:"autoGraded" db:"auto_graded"`
	CreatedAt    time.Time    `json:"createdAt" db:"created_at"`
	UpdatedAt    time.Time    `json:"updatedAt" db:"updated_at"`
}

func NewExamAnswer(sessionID, questionID uuid.UUID, answer string, maxScore float64) *ExamAnswer {
	return &ExamAnswer{
		ID:         uuid.New(),
		SessionID:  sessionID,
		QuestionID: questionID,
		Answer:     answer,
		MaxScore:   maxScore,
		Status:     AnswerStatusPending,
		AutoGraded: false,
		CreatedAt:  time.Now(),
		UpdatedAt:  time.Now(),
	}
}

type AnswerSubmitRequest struct {
	QuestionID string `json:"questionId" binding:"required,uuid"`
	Answer     string `json:"answer" binding:"required"`
}

type AnswerBatchSubmitRequest struct {
	Answers []AnswerSubmitRequest `json:"answers" binding:"required,min=1"`
}

type GradeAnswerRequest struct {
	SessionID  string  `json:"sessionId" binding:"required,uuid"`
	QuestionID string  `json:"questionId" binding:"required,uuid"`
	Score      float64 `json:"score" binding:"required,min=0"`
	Feedback   string  `json:"feedback"`
}

type GradeResponse struct {
	SessionID    uuid.UUID `json:"sessionId"`
	TotalScore   float64   `json:"totalScore"`
	GradedCount  int       `json:"gradedCount"`
	TotalCount   int       `json:"totalCount"`
	IsComplete   bool      `json:"isComplete"`
}
