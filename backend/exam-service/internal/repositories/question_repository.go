package repositories

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/openzhixue/exam-service/internal/models"
)

type QuestionRepository struct {
	db *pgxpool.Pool
}

func NewQuestionRepository(db *pgxpool.Pool) *QuestionRepository {
	return &QuestionRepository{db: db}
}

func (r *QuestionRepository) Create(ctx context.Context, question *models.Question) error {
	query := `
		INSERT INTO questions (id, exam_id, type, content, options, answer, score, 
			question_order, analysis, difficulty, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
	`

	_, err := r.db.Exec(ctx, query,
		question.ID, question.ExamID, question.Type, question.Content,
		question.Options, question.Answer, question.Score, question.Order,
		question.Analysis, question.Difficulty, question.CreatedAt, question.UpdatedAt,
	)

	return err
}

func (r *QuestionRepository) CreateBatch(ctx context.Context, questions []models.Question) error {
	batch := &pgx.Batch{}
	for _, q := range questions {
		batch.Queue(
			`INSERT INTO questions (id, exam_id, type, content, options, answer, score, 
				question_order, analysis, difficulty, created_at, updated_at)
			VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)`,
			q.ID, q.ExamID, q.Type, q.Content, q.Options, q.Answer, q.Score,
			q.Order, q.Analysis, q.Difficulty, q.CreatedAt, q.UpdatedAt,
		)
	}

	results := r.db.SendBatch(ctx, batch)
	defer results.Close()

	for i := 0; i < len(questions); i++ {
		_, err := results.Exec()
		if err != nil {
			return fmt.Errorf("failed to insert question %d: %w", i, err)
		}
	}

	return nil
}

func (r *QuestionRepository) GetByID(ctx context.Context, id uuid.UUID) (*models.Question, error) {
	query := `
		SELECT id, exam_id, type, content, options, answer, score, 
			question_order, analysis, difficulty, created_at, updated_at
		FROM questions WHERE id = $1
	`

	question := &models.Question{}
	err := r.db.QueryRow(ctx, query, id).Scan(
		&question.ID, &question.ExamID, &question.Type, &question.Content,
		&question.Options, &question.Answer, &question.Score, &question.Order,
		&question.Analysis, &question.Difficulty, &question.CreatedAt, &question.UpdatedAt,
	)

	if err != nil {
		if err == pgx.ErrNoRows {
			return nil, sql.ErrNoRows
		}
		return nil, err
	}

	return question, nil
}

func (r *QuestionRepository) GetByExamID(ctx context.Context, examID uuid.UUID) ([]models.Question, error) {
	query := `
		SELECT id, exam_id, type, content, options, answer, score, 
			question_order, analysis, difficulty, created_at, updated_at
		FROM questions WHERE exam_id = $1 ORDER BY question_order
	`

	rows, err := r.db.Query(ctx, query, examID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	questions := []models.Question{}
	for rows.Next() {
		q := models.Question{}
		err := rows.Scan(
			&q.ID, &q.ExamID, &q.Type, &q.Content,
			&q.Options, &q.Answer, &q.Score, &q.Order,
			&q.Analysis, &q.Difficulty, &q.CreatedAt, &q.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		questions = append(questions, q)
	}

	return questions, nil
}

func (r *QuestionRepository) GetByExamIDWithoutAnswers(ctx context.Context, examID uuid.UUID) ([]models.Question, error) {
	query := `
		SELECT id, exam_id, type, content, options, score, 
			question_order, difficulty, created_at, updated_at
		FROM questions WHERE exam_id = $1 ORDER BY question_order
	`

	rows, err := r.db.Query(ctx, query, examID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	questions := []models.Question{}
	for rows.Next() {
		q := models.Question{}
		err := rows.Scan(
			&q.ID, &q.ExamID, &q.Type, &q.Content,
			&q.Options, &q.Score, &q.Order,
			&q.Difficulty, &q.CreatedAt, &q.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		questions = append(questions, q)
	}

	return questions, nil
}

func (r *QuestionRepository) Update(ctx context.Context, question *models.Question) error {
	query := `
		UPDATE questions SET
			type = $2, content = $3, options = $4, answer = $5, score = $6,
			question_order = $7, analysis = $8, difficulty = $9, updated_at = $10
		WHERE id = $1
	`

	result, err := r.db.Exec(ctx, query,
		question.ID, question.Type, question.Content, question.Options,
		question.Answer, question.Score, question.Order, question.Analysis,
		question.Difficulty, question.UpdatedAt,
	)

	if err != nil {
		return err
	}

	if result.RowsAffected() == 0 {
		return sql.ErrNoRows
	}

	return nil
}

func (r *QuestionRepository) Delete(ctx context.Context, id uuid.UUID) error {
	query := `DELETE FROM questions WHERE id = $1`
	result, err := r.db.Exec(ctx, query, id)
	if err != nil {
		return err
	}
	if result.RowsAffected() == 0 {
		return sql.ErrNoRows
	}
	return nil
}

func (r *QuestionRepository) DeleteByExamID(ctx context.Context, examID uuid.UUID) error {
	query := `DELETE FROM questions WHERE exam_id = $1`
	_, err := r.db.Exec(ctx, query, examID)
	return err
}

func (r *QuestionRepository) CountByExamID(ctx context.Context, examID uuid.UUID) (int, error) {
	query := `SELECT COUNT(*) FROM questions WHERE exam_id = $1`
	var count int
	err := r.db.QueryRow(ctx, query, examID).Scan(&count)
	return count, err
}

func (r *QuestionRepository) GetTotalScoreByExamID(ctx context.Context, examID uuid.UUID) (float64, error) {
	query := `SELECT COALESCE(SUM(score), 0) FROM questions WHERE exam_id = $1`
	var total float64
	err := r.db.QueryRow(ctx, query, examID).Scan(&total)
	return total, err
}
