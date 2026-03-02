use async_trait::async_trait;
use sqlx::PgPool;
use uuid::Uuid;
use chrono::Utc;

use crate::error::{ServiceError, ServiceResult};
use crate::models::{
    HomeworkGrade, CreateGradeRequest, UpdateGradeRequest, BatchGradeRequest,
    HomeworkStatistics, ScoreDistribution,
};

pub struct GradeRepository {
    pool: PgPool,
}

impl GradeRepository {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }
}

#[async_trait]
pub trait GradeRepositoryTrait {
    async fn create(&self, submission_id: Uuid, graded_by: Uuid, req: CreateGradeRequest) -> ServiceResult<HomeworkGrade>;
    async fn find_by_id(&self, id: Uuid) -> ServiceResult<HomeworkGrade>;
    async fn find_by_submission(&self, submission_id: Uuid) -> ServiceResult<Option<HomeworkGrade>>;
    async fn update(&self, id: Uuid, req: UpdateGradeRequest) -> ServiceResult<HomeworkGrade>;
    async fn batch_create(&self, graded_by: Uuid, req: BatchGradeRequest) -> ServiceResult<Vec<HomeworkGrade>>;
    async fn get_statistics(&self, homework_id: Uuid) -> ServiceResult<HomeworkStatistics>;
}

#[async_trait]
impl GradeRepositoryTrait for GradeRepository {
    async fn create(&self, submission_id: Uuid, graded_by: Uuid, req: CreateGradeRequest) -> ServiceResult<HomeworkGrade> {
        let id = Uuid::new_v4();
        let now = Utc::now();

        let grade = sqlx::query_as!(
            HomeworkGrade,
            r#"
            INSERT INTO homework_grades (id, submission_id, score, max_score, comment, graded_by, graded_at, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id, submission_id, score, max_score, comment, graded_by, graded_at, created_at
            "#,
            id, submission_id, req.score, req.max_score, req.comment, graded_by, now, now
        )
        .fetch_one(&self.pool)
        .await?;

        sqlx::query(
            "UPDATE homework_submissions SET status = 'graded', updated_at = $1 WHERE id = $2"
        )
        .bind(now)
        .bind(submission_id)
        .execute(&self.pool)
        .await?;

        Ok(grade)
    }

    async fn find_by_id(&self, id: Uuid) -> ServiceResult<HomeworkGrade> {
        let grade = sqlx::query_as!(
            HomeworkGrade,
            r#"
            SELECT id, submission_id, score, max_score, comment, graded_by, graded_at, created_at
            FROM homework_grades
            WHERE id = $1
            "#,
            id
        )
        .fetch_optional(&self.pool)
        .await?
        .ok_or_else(|| ServiceError::NotFound(format!("Grade with id {} not found", id)))?;

        Ok(grade)
    }

    async fn find_by_submission(&self, submission_id: Uuid) -> ServiceResult<Option<HomeworkGrade>> {
        let grade = sqlx::query_as!(
            HomeworkGrade,
            r#"
            SELECT id, submission_id, score, max_score, comment, graded_by, graded_at, created_at
            FROM homework_grades
            WHERE submission_id = $1
            "#,
            submission_id
        )
        .fetch_optional(&self.pool)
        .await?;

        Ok(grade)
    }

    async fn update(&self, id: Uuid, req: UpdateGradeRequest) -> ServiceResult<HomeworkGrade> {
        let now = Utc::now();

        let grade = sqlx::query_as!(
            HomeworkGrade,
            r#"
            UPDATE homework_grades
            SET score = COALESCE($1, score),
                max_score = COALESCE($2, max_score),
                comment = COALESCE($3, comment),
                graded_at = $4
            WHERE id = $5
            RETURNING id, submission_id, score, max_score, comment, graded_by, graded_at, created_at
            "#,
            req.score, req.max_score, req.comment, now, id
        )
        .fetch_optional(&self.pool)
        .await?
        .ok_or_else(|| ServiceError::NotFound(format!("Grade with id {} not found", id)))?;

        Ok(grade)
    }

    async fn batch_create(&self, graded_by: Uuid, req: BatchGradeRequest) -> ServiceResult<Vec<HomeworkGrade>> {
        let mut grades = Vec::new();
        let now = Utc::now();

        for item in req.grades {
            let id = Uuid::new_v4();
            
            let grade = sqlx::query_as!(
                HomeworkGrade,
                r#"
                INSERT INTO homework_grades (id, submission_id, score, max_score, comment, graded_by, graded_at, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id, submission_id, score, max_score, comment, graded_by, graded_at, created_at
                "#,
                id, item.submission_id, item.score, item.max_score, item.comment, graded_by, now, now
            )
            .fetch_one(&self.pool)
            .await?;

            sqlx::query(
                "UPDATE homework_submissions SET status = 'graded', updated_at = $1 WHERE id = $2"
            )
            .bind(now)
            .bind(item.submission_id)
            .execute(&self.pool)
            .await?;

            grades.push(grade);
        }

        Ok(grades)
    }

    async fn get_statistics(&self, homework_id: Uuid) -> ServiceResult<HomeworkStatistics> {
        let total_students: i64 = sqlx::query_scalar(
            "SELECT COUNT(DISTINCT student_id) FROM homework_submissions WHERE homework_id = $1"
        )
        .bind(homework_id)
        .fetch_one(&self.pool)
        .await?;

        let submitted_count: i64 = sqlx::query_scalar(
            "SELECT COUNT(*) FROM homework_submissions WHERE homework_id = $1"
        )
        .bind(homework_id)
        .fetch_one(&self.pool)
        .await?;

        let graded_count: i64 = sqlx::query_scalar(
            r#"
            SELECT COUNT(*) FROM homework_submissions hs
            JOIN homework_grades hg ON hs.id = hg.submission_id
            WHERE hs.homework_id = $1
            "#
        )
        .bind(homework_id)
        .fetch_one(&self.pool)
        .await?;

        let score_stats: Option<(Option<f64>, Option<f64>, Option<f64>)> = sqlx::query_as(
            r#"
            SELECT AVG(hg.score), MAX(hg.score), MIN(hg.score)
            FROM homework_submissions hs
            JOIN homework_grades hg ON hs.id = hg.submission_id
            WHERE hs.homework_id = $1
            "#
        )
        .bind(homework_id)
        .fetch_one(&self.pool)
        .await?;

        let (average_score, highest_score, lowest_score) = score_stats.unwrap_or((None, None, None));

        let scores: Vec<f64> = sqlx::query_scalar(
            r#"
            SELECT (hg.score / hg.max_score) * 100 as percentage
            FROM homework_submissions hs
            JOIN homework_grades hg ON hs.id = hg.submission_id
            WHERE hs.homework_id = $1 AND hg.max_score > 0
            "#
        )
        .bind(homework_id)
        .fetch_all(&self.pool)
        .await?;

        let mut score_distribution = ScoreDistribution::new();
        for score in scores {
            score_distribution.add_score(score);
        }

        let submission_rate = if total_students > 0 {
            (submitted_count as f64) / (total_students as f64) * 100.0
        } else {
            0.0
        };

        Ok(HomeworkStatistics {
            homework_id,
            total_students,
            submitted_count,
            graded_count,
            average_score,
            highest_score,
            lowest_score,
            submission_rate,
            score_distribution,
        })
    }
}
