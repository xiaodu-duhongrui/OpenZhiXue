package models

import (
	"database/sql/driver"
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

type QuestionType string

const (
	QuestionTypeSingleChoice  QuestionType = "single_choice"
	QuestionTypeMultipleChoice QuestionType = "multiple_choice"
	QuestionTypeTrueFalse     QuestionType = "true_false"
	QuestionTypeFillBlank     QuestionType = "fill_blank"
	QuestionTypeShortAnswer   QuestionType = "short_answer"
	QuestionTypeEssay         QuestionType = "essay"
	QuestionTypeMatching      QuestionType = "matching"
	QuestionTypeOrdering      QuestionType = "ordering"
)

type QuestionOption struct {
	ID      string `json:"id"`
	Content string `json:"content"`
	IsCorrect bool   `json:"isCorrect,omitempty"`
}

type QuestionOptions []QuestionOption

func (o QuestionOptions) Value() (driver.Value, error) {
	return json.Marshal(o)
}

func (o *QuestionOptions) Scan(value interface{}) error {
	if value == nil {
		*o = QuestionOptions{}
		return nil
	}
	bytes, ok := value.([]byte)
	if !ok {
		return nil
	}
	return json.Unmarshal(bytes, o)
}

type Question struct {
	ID         uuid.UUID      `json:"id" db:"id"`
	ExamID     uuid.UUID      `json:"examId" db:"exam_id"`
	Type       QuestionType   `json:"type" db:"type"`
	Content    string         `json:"content" db:"content"`
	Options    QuestionOptions `json:"options" db:"options"`
	Answer     string         `json:"answer" db:"answer"`
	Score      float64        `json:"score" db:"score"`
	Order      int            `json:"order" db:"question_order"`
	Analysis   string         `json:"analysis" db:"analysis"`
	Difficulty int            `json:"difficulty" db:"difficulty"`
	CreatedAt  time.Time      `json:"createdAt" db:"created_at"`
	UpdatedAt  time.Time      `json:"updatedAt" db:"updated_at"`
}

func NewQuestion() *Question {
	return &Question{
		ID:        uuid.New(),
		Options:   QuestionOptions{},
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
}

type QuestionCreateRequest struct {
	ExamID     string          `json:"examId" binding:"required,uuid"`
	Type       QuestionType    `json:"type" binding:"required"`
	Content    string          `json:"content" binding:"required"`
	Options    QuestionOptions `json:"options"`
	Answer     string          `json:"answer" binding:"required"`
	Score      float64         `json:"score" binding:"required,min=0"`
	Order      int             `json:"order" binding:"min=1"`
	Analysis   string          `json:"analysis"`
	Difficulty int             `json:"difficulty" binding:"min=1,max=5"`
}

type QuestionUpdateRequest struct {
	Type       QuestionType    `json:"type"`
	Content    string          `json:"content"`
	Options    QuestionOptions `json:"options"`
	Answer     string          `json:"answer"`
	Score      float64         `json:"score"`
	Order      int             `json:"order"`
	Analysis   string          `json:"analysis"`
	Difficulty int             `json:"difficulty"`
}

type QuestionBatchCreateRequest struct {
	ExamID    string                  `json:"examId" binding:"required,uuid"`
	Questions []QuestionCreateRequest `json:"questions" binding:"required,min=1"`
}

type QuestionResponse struct {
	Question
	StudentAnswer string  `json:"studentAnswer,omitempty"`
	StudentScore  float64 `json:"studentScore,omitempty"`
	IsCorrect     bool    `json:"isCorrect,omitempty"`
}

func (q *Question) IsObjective() bool {
	switch q.Type {
	case QuestionTypeSingleChoice, QuestionTypeMultipleChoice, QuestionTypeTrueFalse, QuestionTypeFillBlank:
		return true
	default:
		return false
	}
}

func (q *Question) CheckAnswer(studentAnswer string) (bool, float64) {
	if !q.IsObjective() {
		return false, 0
	}

	switch q.Type {
	case QuestionTypeSingleChoice, QuestionTypeTrueFalse:
		if studentAnswer == q.Answer {
			return true, q.Score
		}
	case QuestionTypeMultipleChoice:
		if studentAnswer == q.Answer {
			return true, q.Score
		}
	case QuestionTypeFillBlank:
		if studentAnswer == q.Answer {
			return true, q.Score
		}
	}
	return false, 0
}
