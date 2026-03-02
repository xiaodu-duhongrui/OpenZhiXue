package repositories

import (
	"context"
	"database/sql"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/openzhixue/exam-service/internal/models"
)

type AnswerRepository struct {
	db *pgxpool.Pool
}

func NewAnswerRepository(db *pgxpool.Pool) *AnswerRepository {
	return &AnswerRepository{db: db}
}

func (r *AnswerRepository) Create(ctx context.Context, answer *models.ExamAnswer) error {
	query := `
		INSERT INTO exam_answers (id, session_id, question_id, answer, score, max_score, 
			status, auto_graded, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
		ON CONFLICT (session_id, question_id) DO UPDATE SET
			answer = EXCLUDED.answer,
			score = EXCLUDED.score,
			status = EXCLUDED.status,
			auto_graded = EXCLUDED.auto_graded,
			updated_at = EXCLUDED.updated_at
	`

	_, err := r.db.Exec(ctx, query,
		answer.ID, answer.SessionID, answer.QuestionID, answer.Answer,
		answer.Score, answer.MaxScore, answer.Status, answer.AutoGraded,
		answer.CreatedAt, answer.UpdatedAt,
	)

	return err
}

func (r *AnswerRepository) CreateBatch(ctx context.Context, answers []models.ExamAnswer) error {
	for _, a := range answers {
		if err := r.Create(ctx, &a); err != nil {
			return err
		}
	}
	return nil
}

func (r *AnswerRepository) GetByID(ctx context.Context, id uuid.UUID) (*models.ExamAnswer, error) {
	query := `
		SELECT id, session_id, question_id, answer, score, max_score,
			status, graded_by, graded_at, feedback, auto_graded, created_at, updated_at
		FROM exam_answers WHERE id = $1
	`

	answer := &models.ExamAnswer{}
	err := r.db.QueryRow(ctx, query, id).Scan(
		&answer.ID, &answer.SessionID, &answer.QuestionID, &answer.Answer,
		&answer.Score, &answer.MaxScore, &answer.Status, &answer.GradedBy,
		&answer.GradedAt, &answer.Feedback, &answer.AutoGraded,
		&answer.CreatedAt, &answer.UpdatedAt,
	)

	if err != nil {
		if err == pgx.ErrNoRows {
			return nil, sql.ErrNoRows
		}
		return nil, err
	}

	return answer, nil
}

func (r *AnswerRepository) GetBySessionAndQuestion(ctx context.Context, sessionID, questionID uuid.UUID) (*models.ExamAnswer, error) {
	query := `
		SELECT id, session_id, question_id, answer, score, max_score,
			status, graded_by, graded_at, feedback, auto_graded, created_at, updated_at
		FROM exam_answers WHERE session_id = $1 AND question_id = $2
	`

	answer := &models.ExamAnswer{}
	err := r.db.QueryRow(ctx, query, sessionID, questionID).Scan(
		&answer.ID, &answer.SessionID, &answer.QuestionID, &answer.Answer,
		&answer.Score, &answer.MaxScore, &answer.Status, &answer.GradedBy,
		&answer.GradedAt, &answer.Feedback, &answer.AutoGraded,
		&answer.CreatedAt, &answer.UpdatedAt,
	)

	if err != nil {
		if err == pgx.ErrNoRows {
			return nil, sql.ErrNoRows
		}
		return nil, err
	}

	return answer, nil
}

func (r *AnswerRepository) GetBySessionID(ctx context.Context, sessionID uuid.UUID) ([]models.ExamAnswer, error) {
	query := `
		SELECT id, session_id, question_id, answer, score, max_score,
			status, graded_by, graded_at, feedback, auto_graded, created_at, updated_at
		FROM exam_answers WHERE session_id = $1
	`

	rows, err := r.db.Query(ctx, query, sessionID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	answers := []models.ExamAnswer{}
	for rows.Next() {
		a := models.ExamAnswer{}
		err := rows.Scan(
			&a.ID, &a.SessionID, &a.QuestionID, &a.Answer,
			&a.Score, &a.MaxScore, &a.Status, &a.GradedBy,
			&a.GradedAt, &a.Feedback, &a.AutoGraded,
			&a.CreatedAt, &a.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		answers = append(answers, a)
	}

	return answers, nil
}

func (r *AnswerRepository) Update(ctx context.Context, answer *models.ExamAnswer) error {
	query := `
		UPDATE exam_answers SET
			answer = $2, score = $3, status = $4, graded_by = $5,
			graded_at = $6, feedback = $7, auto_graded = $8, updated_at = $9
		WHERE id = $1
	`

	answer.UpdatedAt = time.Now()

	result, err := r.db.Exec(ctx, query,
		answer.ID, answer.Answer, answer.Score, answer.Status, answer.GradedBy,
		answer.GradedAt, answer.Feedback, answer.AutoGraded, answer.UpdatedAt,
	)

	if err != nil {
		return err
	}

	if result.RowsAffected() == 0 {
		return sql.ErrNoRows
	}

	return nil
}

func (r *AnswerRepository) UpdateScore(ctx context.Context, id uuid.UUID, score float64, status models.AnswerStatus, gradedBy uuid.UUID, feedback string) error {
	query := `
		UPDATE exam_answers SET
			score = $2, status = $3, graded_by = $4, graded_at = $5,
			feedback = $6, auto_graded = false, updated_at = $7
		WHERE id = $1
	`

	result, err := r.db.Exec(ctx, query, id, score, status, gradedBy, time.Now(), feedback, time.Now())
	if err != nil {
		return err
	}
	if result.RowsAffected() == 0 {
		return sql.ErrNoRows
	}
	return nil
}

func (r *AnswerRepository) DeleteBySessionID(ctx context.Context, sessionID uuid.UUID) error {
	query := `DELETE FROM exam_answers WHERE session_id = $1`
	_, err := r.db.Exec(ctx, query, sessionID)
	return err
}

func (r *AnswerRepository) CountGradedBySession(ctx context.Context, sessionID uuid.UUID) (int, error) {
	query := `SELECT COUNT(*) FROM exam_answers WHERE session_id = $1 AND status != 'pending'`
	var count int
	err := r.db.QueryRow(ctx, query, sessionID).Scan(&count)
	return count, err
}

func (r *AnswerRepository) CountTotalBySession(ctx context.Context, sessionID uuid.UUID) (int, error) {
	query := `SELECT COUNT(*) FROM exam_answers WHERE session_id = $1`
	var count int
	err := r.db.QueryRow(ctx, query, sessionID).Scan(&count)
	return count, err
}

func (r *AnswerRepository) GetTotalScoreBySession(ctx context.Context, sessionID uuid.UUID) (float64, error) {
	query := `SELECT COALESCE(SUM(score), 0) FROM exam_answers WHERE session_id = $1`
	var total float64
	err := r.db.QueryRow(ctx, query, sessionID).Scan(&total)
	return total, err
}

func (r *AnswerRepository) GetQuestionStats(ctx context.Context, questionID uuid.UUID) (*models.QuestionStatistics, error) {
	query := `
		SELECT 
			COUNT(*) as total_attempts,
			COUNT(*) FILTER (WHERE status = 'correct') as correct_count,
			COUNT(*) FILTER (WHERE status = 'wrong') as wrong_count,
			COUNT(*) FILTER (WHERE status = 'partial') as partial_count,
			COALESCE(AVG(score), 0) as avg_score,
			MAX(max_score) as max_score
		FROM exam_answers WHERE question_id = $1
	`

	stats := &models.QuestionStatistics{QuestionID: questionID}
	err := r.db.QueryRow(ctx, query, questionID).Scan(
		&stats.TotalAttempts, &stats.CorrectCount, &stats.WrongCount,
		&stats.PartialCount, &stats.AverageScore, &stats.MaxScore,
	)

	if err != nil {
		return nil, err
	}

	if stats.TotalAttempts > 0 {
		stats.CorrectRate = float64(stats.CorrectCount) / float64(stats.TotalAttempts)
	}

	return stats, nil
}
