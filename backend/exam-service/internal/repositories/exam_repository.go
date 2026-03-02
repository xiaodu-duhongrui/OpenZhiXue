package repositories

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/openzhixue/exam-service/internal/models"
)

type ExamRepository struct {
	db *pgxpool.Pool
}

func NewExamRepository(db *pgxpool.Pool) *ExamRepository {
	return &ExamRepository{db: db}
}

func (r *ExamRepository) Create(ctx context.Context, exam *models.Exam) error {
	query := `
		INSERT INTO exams (id, name, type, subject_ids, class_ids, start_time, end_time, 
			duration, status, total_score, pass_score, description, created_by, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
	`

	subjectIDs, _ := json.Marshal(exam.SubjectIDs)
	classIDs, _ := json.Marshal(exam.ClassIDs)

	_, err := r.db.Exec(ctx, query,
		exam.ID, exam.Name, exam.Type, subjectIDs, classIDs,
		exam.StartTime, exam.EndTime, exam.Duration, exam.Status,
		exam.TotalScore, exam.PassScore, exam.Description,
		exam.CreatedBy, exam.CreatedAt, exam.UpdatedAt,
	)

	return err
}

func (r *ExamRepository) GetByID(ctx context.Context, id uuid.UUID) (*models.Exam, error) {
	query := `
		SELECT id, name, type, subject_ids, class_ids, start_time, end_time,
			duration, status, total_score, pass_score, description, created_by, created_at, updated_at
		FROM exams WHERE id = $1
	`

	exam := &models.Exam{}
	var subjectIDs, classIDs []byte

	err := r.db.QueryRow(ctx, query, id).Scan(
		&exam.ID, &exam.Name, &exam.Type, &subjectIDs, &classIDs,
		&exam.StartTime, &exam.EndTime, &exam.Duration, &exam.Status,
		&exam.TotalScore, &exam.PassScore, &exam.Description,
		&exam.CreatedBy, &exam.CreatedAt, &exam.UpdatedAt,
	)

	if err != nil {
		if err == pgx.ErrNoRows {
			return nil, sql.ErrNoRows
		}
		return nil, err
	}

	json.Unmarshal(subjectIDs, &exam.SubjectIDs)
	json.Unmarshal(classIDs, &exam.ClassIDs)

	return exam, nil
}

func (r *ExamRepository) Update(ctx context.Context, exam *models.Exam) error {
	query := `
		UPDATE exams SET
			name = $2, type = $3, subject_ids = $4, class_ids = $5,
			start_time = $6, end_time = $7, duration = $8, status = $9,
			total_score = $10, pass_score = $11, description = $12, updated_at = $13
		WHERE id = $1
	`

	subjectIDs, _ := json.Marshal(exam.SubjectIDs)
	classIDs, _ := json.Marshal(exam.ClassIDs)
	exam.UpdatedAt = time.Now()

	result, err := r.db.Exec(ctx, query,
		exam.ID, exam.Name, exam.Type, subjectIDs, classIDs,
		exam.StartTime, exam.EndTime, exam.Duration, exam.Status,
		exam.TotalScore, exam.PassScore, exam.Description, exam.UpdatedAt,
	)

	if err != nil {
		return err
	}

	if result.RowsAffected() == 0 {
		return sql.ErrNoRows
	}

	return nil
}

func (r *ExamRepository) Delete(ctx context.Context, id uuid.UUID) error {
	query := `DELETE FROM exams WHERE id = $1`
	result, err := r.db.Exec(ctx, query, id)
	if err != nil {
		return err
	}
	if result.RowsAffected() == 0 {
		return sql.ErrNoRows
	}
	return nil
}

func (r *ExamRepository) List(ctx context.Context, filter *models.ExamFilter) ([]models.Exam, int64, error) {
	baseQuery := `FROM exams WHERE 1=1`
	args := []interface{}{}
	argIndex := 1

	if filter.Status != "" {
		baseQuery += fmt.Sprintf(" AND status = $%d", argIndex)
		args = append(args, filter.Status)
		argIndex++
	}

	if filter.Type != "" {
		baseQuery += fmt.Sprintf(" AND type = $%d", argIndex)
		args = append(args, filter.Type)
		argIndex++
	}

	if filter.SubjectID != "" {
		baseQuery += fmt.Sprintf(" AND $%d = ANY(subject_ids)", argIndex)
		args = append(args, filter.SubjectID)
		argIndex++
	}

	if filter.ClassID != "" {
		baseQuery += fmt.Sprintf(" AND $%d = ANY(class_ids)", argIndex)
		args = append(args, filter.ClassID)
		argIndex++
	}

	if filter.StartDate != "" {
		baseQuery += fmt.Sprintf(" AND start_time >= $%d", argIndex)
		args = append(args, filter.StartDate)
		argIndex++
	}

	if filter.EndDate != "" {
		baseQuery += fmt.Sprintf(" AND end_time <= $%d", argIndex)
		args = append(args, filter.EndDate)
		argIndex++
	}

	countQuery := `SELECT COUNT(*) ` + baseQuery
	var total int64
	err := r.db.QueryRow(ctx, countQuery, args...).Scan(&total)
	if err != nil {
		return nil, 0, err
	}

	if filter.Page < 1 {
		filter.Page = 1
	}
	if filter.PageSize < 1 {
		filter.PageSize = 10
	}

	offset := (filter.Page - 1) * filter.PageSize
	listQuery := `SELECT id, name, type, subject_ids, class_ids, start_time, end_time,
		duration, status, total_score, pass_score, description, created_by, created_at, updated_at ` +
		baseQuery + ` ORDER BY created_at DESC LIMIT $%d OFFSET $%d`

	args = append(args, filter.PageSize, offset)
	listQuery = fmt.Sprintf(listQuery, argIndex, argIndex+1)

	rows, err := r.db.Query(ctx, listQuery, args...)
	if err != nil {
		return nil, 0, err
	}
	defer rows.Close()

	exams := []models.Exam{}
	for rows.Next() {
		exam := models.Exam{}
		var subjectIDs, classIDs []byte
		err := rows.Scan(
			&exam.ID, &exam.Name, &exam.Type, &subjectIDs, &classIDs,
			&exam.StartTime, &exam.EndTime, &exam.Duration, &exam.Status,
			&exam.TotalScore, &exam.PassScore, &exam.Description,
			&exam.CreatedBy, &exam.CreatedAt, &exam.UpdatedAt,
		)
		if err != nil {
			return nil, 0, err
		}
		json.Unmarshal(subjectIDs, &exam.SubjectIDs)
		json.Unmarshal(classIDs, &exam.ClassIDs)
		exams = append(exams, exam)
	}

	return exams, total, nil
}

func (r *ExamRepository) UpdateStatus(ctx context.Context, id uuid.UUID, status models.ExamStatus) error {
	query := `UPDATE exams SET status = $2, updated_at = $3 WHERE id = $1`
	result, err := r.db.Exec(ctx, query, id, status, time.Now())
	if err != nil {
		return err
	}
	if result.RowsAffected() == 0 {
		return sql.ErrNoRows
	}
	return nil
}

func (r *ExamRepository) GetByClassID(ctx context.Context, classID string) ([]models.Exam, error) {
	query := `
		SELECT id, name, type, subject_ids, class_ids, start_time, end_time,
			duration, status, total_score, pass_score, description, created_by, created_at, updated_at
		FROM exams WHERE $1 = ANY(class_ids) AND status != 'draft'
	`

	rows, err := r.db.Query(ctx, query, classID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	exams := []models.Exam{}
	for rows.Next() {
		exam := models.Exam{}
		var subjectIDs, classIDs []byte
		err := rows.Scan(
			&exam.ID, &exam.Name, &exam.Type, &subjectIDs, &classIDs,
			&exam.StartTime, &exam.EndTime, &exam.Duration, &exam.Status,
			&exam.TotalScore, &exam.PassScore, &exam.Description,
			&exam.CreatedBy, &exam.CreatedAt, &exam.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		json.Unmarshal(subjectIDs, &exam.SubjectIDs)
		json.Unmarshal(classIDs, &exam.ClassIDs)
		exams = append(exams, exam)
	}

	return exams, nil
}
