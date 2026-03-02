package exam

import (
	"context"
	"time"

	"github.com/google/uuid"
)

type ExamStatus string

const (
	StatusDraft     ExamStatus = "draft"
	StatusPublished ExamStatus = "published"
	StatusOngoing   ExamStatus = "ongoing"
	StatusEnded     ExamStatus = "ended"
)

type ExamInfo struct {
	ID          uuid.UUID   `json:"id"`
	Name        string      `json:"name"`
	Status      ExamStatus  `json:"status"`
	StartTime   time.Time   `json:"startTime"`
	EndTime     time.Time   `json:"endTime"`
	Duration    int         `json:"duration"`
	TotalScore  float64     `json:"totalScore"`
}

type QuestionInfo struct {
	ID         uuid.UUID `json:"id"`
	Type       string    `json:"type"`
	Content    string    `json:"content"`
	Score      float64   `json:"score"`
	Order      int       `json:"order"`
}

type SessionInfo struct {
	ID            uuid.UUID `json:"id"`
	ExamID        uuid.UUID `json:"examId"`
	StudentID     uuid.UUID `json:"studentId"`
	StartTime     time.Time `json:"startTime"`
	EndTime       time.Time `json:"endTime"`
	RemainingTime int       `json:"remainingTime"`
	Status        string    `json:"status"`
}

type AnswerInfo struct {
	QuestionID uuid.UUID `json:"questionId"`
	Answer     string    `json:"answer"`
	Score      float64   `json:"score"`
}

type ResultInfo struct {
	SessionID  uuid.UUID     `json:"sessionId"`
	TotalScore float64       `json:"totalScore"`
	MaxScore   float64       `json:"maxScore"`
	Percentage float64       `json:"percentage"`
	Rank       int           `json:"rank"`
	Passed     bool          `json:"passed"`
	Answers    []AnswerInfo  `json:"answers"`
}

type ExamServiceClient interface {
	GetExam(ctx context.Context, examID uuid.UUID) (*ExamInfo, error)
	GetQuestions(ctx context.Context, examID uuid.UUID) ([]QuestionInfo, error)
	StartSession(ctx context.Context, examID, studentID uuid.UUID) (*SessionInfo, error)
	GetSession(ctx context.Context, sessionID uuid.UUID) (*SessionInfo, error)
	SubmitAnswer(ctx context.Context, sessionID, questionID uuid.UUID, answer string) error
	SubmitExam(ctx context.Context, sessionID uuid.UUID) (*ResultInfo, error)
	GetResult(ctx context.Context, sessionID uuid.UUID) (*ResultInfo, error)
}
