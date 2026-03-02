package models

import (
	"time"

	"github.com/google/uuid"
)

type ExamStatistics struct {
	ExamID             uuid.UUID `json:"examId"`
	TotalParticipants  int       `json:"totalParticipants"`
	SubmittedCount     int       `json:"submittedCount"`
	AverageScore       float64   `json:"averageScore"`
	MaxScore           float64   `json:"maxScore"`
	MinScore           float64   `json:"minScore"`
	MedianScore        float64   `json:"medianScore"`
	StandardDeviation  float64   `json:"standardDeviation"`
	PassRate           float64   `json:"passRate"`
	CompletionRate     float64   `json:"completionRate"`
	AverageDuration    int       `json:"averageDuration"`
	GeneratedAt        time.Time `json:"generatedAt"`
}

type QuestionStatistics struct {
	QuestionID       uuid.UUID `json:"questionId"`
	QuestionOrder    int       `json:"questionOrder"`
	QuestionType     string    `json:"questionType"`
	TotalAttempts    int       `json:"totalAttempts"`
	CorrectCount     int       `json:"correctCount"`
	WrongCount       int       `json:"wrongCount"`
	PartialCount     int       `json:"partialCount"`
	CorrectRate      float64   `json:"correctRate"`
	AverageScore     float64   `json:"averageScore"`
	MaxScore         float64   `json:"maxScore"`
	DiscriminationIndex float64 `json:"discriminationIndex"`
}

type ScoreDistribution struct {
	ScoreRange string `json:"scoreRange"`
	Count      int    `json:"count"`
	Percentage float64 `json:"percentage"`
}

type ExamAnalysis struct {
	ExamID            uuid.UUID           `json:"examId"`
	Statistics        ExamStatistics      `json:"statistics"`
	QuestionStats     []QuestionStatistics `json:"questionStats"`
	ScoreDistribution []ScoreDistribution `json:"scoreDistribution"`
	TopPerformers     []StudentScore      `json:"topPerformers"`
	BottomPerformers  []StudentScore      `json:"bottomPerformers"`
	GeneratedAt       time.Time           `json:"generatedAt"`
}

type StudentScore struct {
	StudentID   uuid.UUID `json:"studentId"`
	StudentName string    `json:"studentName"`
	Score       float64   `json:"score"`
	Rank        int       `json:"rank"`
	Percentile  float64   `json:"percentile"`
}

type StudentResult struct {
	SessionID      uuid.UUID       `json:"sessionId"`
	ExamID         uuid.UUID       `json:"examId"`
	StudentID      uuid.UUID       `json:"studentId"`
	TotalScore     float64         `json:"totalScore"`
	MaxScore       float64         `json:"maxScore"`
	Percentage     float64         `json:"percentage"`
	Rank           int             `json:"rank"`
	Percentile     float64         `json:"percentile"`
	Passed         bool            `json:"passed"`
	Answers        []AnswerResult  `json:"answers"`
	SubmittedAt    time.Time       `json:"submittedAt"`
	Duration       int             `json:"duration"`
}

type AnswerResult struct {
	QuestionID     uuid.UUID `json:"questionId"`
	QuestionOrder  int       `json:"questionOrder"`
	QuestionType   string    `json:"questionType"`
	StudentAnswer  string    `json:"studentAnswer"`
	CorrectAnswer  string    `json:"correctAnswer"`
	Score          float64   `json:"score"`
	MaxScore       float64   `json:"maxScore"`
	IsCorrect      bool      `json:"isCorrect"`
	Feedback       string    `json:"feedback"`
}

type RankingResponse struct {
	Rankings []StudentScore `json:"rankings"`
	Total    int            `json:"total"`
	Page     int            `json:"page"`
	PageSize int            `json:"pageSize"`
}
