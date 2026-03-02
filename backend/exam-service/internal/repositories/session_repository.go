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

type SessionRepository struct {
	db *pgxpool.Pool
}

func NewSessionRepository(db *pgxpool.Pool) *SessionRepository {
	return &SessionRepository{db: db}
}

func (r *SessionRepository) Create(ctx context.Context, session *models.ExamSession) error {
	query := `
		INSERT INTO exam_sessions (id, exam_id, student_id, start_time, end_time, 
			status, ip_address, user_agent, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
	`

	_, err := r.db.Exec(ctx, query,
		session.ID, session.ExamID, session.StudentID, session.StartTime, session.EndTime,
		session.Status, session.IPAddress, session.UserAgent, session.CreatedAt, session.UpdatedAt,
	)

	return err
}

func (r *SessionRepository) GetByID(ctx context.Context, id uuid.UUID) (*models.ExamSession, error) {
	query := `
		SELECT id, exam_id, student_id, start_time, submit_time, end_time,
			status, total_score, elapsed_time, ip_address, user_agent, created_at, updated_at
		FROM exam_sessions WHERE id = $1
	`

	session := &models.ExamSession{}
	err := r.db.QueryRow(ctx, query, id).Scan(
		&session.ID, &session.ExamID, &session.StudentID, &session.StartTime, &session.SubmitTime,
		&session.EndTime, &session.Status, &session.TotalScore, &session.ElapsedTime,
		&session.IPAddress, &session.UserAgent, &session.CreatedAt, &session.UpdatedAt,
	)

	if err != nil {
		if err == pgx.ErrNoRows {
			return nil, sql.ErrNoRows
		}
		return nil, err
	}

	return session, nil
}

func (r *SessionRepository) GetByExamAndStudent(ctx context.Context, examID, studentID uuid.UUID) (*models.ExamSession, error) {
	query := `
		SELECT id, exam_id, student_id, start_time, submit_time, end_time,
			status, total_score, elapsed_time, ip_address, user_agent, created_at, updated_at
		FROM exam_sessions WHERE exam_id = $1 AND student_id = $2
	`

	session := &models.ExamSession{}
	err := r.db.QueryRow(ctx, query, examID, studentID).Scan(
		&session.ID, &session.ExamID, &session.StudentID, &session.StartTime, &session.SubmitTime,
		&session.EndTime, &session.Status, &session.TotalScore, &session.ElapsedTime,
		&session.IPAddress, &session.UserAgent, &session.CreatedAt, &session.UpdatedAt,
	)

	if err != nil {
		if err == pgx.ErrNoRows {
			return nil, sql.ErrNoRows
		}
		return nil, err
	}

	return session, nil
}

func (r *SessionRepository) Update(ctx context.Context, session *models.ExamSession) error {
	query := `
		UPDATE exam_sessions SET
			start_time = $2, submit_time = $3, end_time = $4, status = $5,
			total_score = $6, elapsed_time = $7, updated_at = $8
		WHERE id = $1
	`

	session.UpdatedAt = time.Now()

	result, err := r.db.Exec(ctx, query,
		session.ID, session.StartTime, session.SubmitTime, session.EndTime,
		session.Status, session.TotalScore, session.ElapsedTime, session.UpdatedAt,
	)

	if err != nil {
		return err
	}

	if result.RowsAffected() == 0 {
		return sql.ErrNoRows
	}

	return nil
}

func (r *SessionRepository) UpdateStatus(ctx context.Context, id uuid.UUID, status models.SessionStatus) error {
	query := `UPDATE exam_sessions SET status = $2, updated_at = $3 WHERE id = $1`
	result, err := r.db.Exec(ctx, query, id, status, time.Now())
	if err != nil {
		return err
	}
	if result.RowsAffected() == 0 {
		return sql.ErrNoRows
	}
	return nil
}

func (r *SessionRepository) Submit(ctx context.Context, id uuid.UUID, totalScore float64) error {
	query := `
		UPDATE exam_sessions SET 
			submit_time = $2, status = $3, total_score = $4, updated_at = $5
		WHERE id = $1
	`

	result, err := r.db.Exec(ctx, query, id, time.Now(), models.SessionStatusSubmitted, totalScore, time.Now())
	if err != nil {
		return err
	}
	if result.RowsAffected() == 0 {
		return sql.ErrNoRows
	}
	return nil
}

func (r *SessionRepository) GetByExamID(ctx context.Context, examID uuid.UUID) ([]models.ExamSession, error) {
	query := `
		SELECT id, exam_id, student_id, start_time, submit_time, end_time,
			status, total_score, elapsed_time, ip_address, user_agent, created_at, updated_at
		FROM exam_sessions WHERE exam_id = $1 ORDER BY created_at DESC
	`

	rows, err := r.db.Query(ctx, query, examID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	sessions := []models.ExamSession{}
	for rows.Next() {
		s := models.ExamSession{}
		err := rows.Scan(
			&s.ID, &s.ExamID, &s.StudentID, &s.StartTime, &s.SubmitTime,
			&s.EndTime, &s.Status, &s.TotalScore, &s.ElapsedTime,
			&s.IPAddress, &s.UserAgent, &s.CreatedAt, &s.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		sessions = append(sessions, s)
	}

	return sessions, nil
}

func (r *SessionRepository) CountByExamID(ctx context.Context, examID uuid.UUID) (int, error) {
	query := `SELECT COUNT(*) FROM exam_sessions WHERE exam_id = $1`
	var count int
	err := r.db.QueryRow(ctx, query, examID).Scan(&count)
	return count, err
}

func (r *SessionRepository) CountSubmittedByExamID(ctx context.Context, examID uuid.UUID) (int, error) {
	query := `SELECT COUNT(*) FROM exam_sessions WHERE exam_id = $1 AND status IN ('submitted', 'graded')`
	var count int
	err := r.db.QueryRow(ctx, query, examID).Scan(&count)
	return count, err
}

func (r *SessionRepository) GetScoresByExamID(ctx context.Context, examID uuid.UUID) ([]float64, error) {
	query := `
		SELECT total_score FROM exam_sessions 
		WHERE exam_id = $1 AND status IN ('submitted', 'graded')
		ORDER BY total_score DESC
	`

	rows, err := r.db.Query(ctx, query, examID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	scores := []float64{}
	for rows.Next() {
		var score float64
		if err := rows.Scan(&score); err != nil {
			return nil, err
		}
		scores = append(scores, score)
	}

	return scores, nil
}
