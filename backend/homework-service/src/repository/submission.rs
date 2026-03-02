use async_trait::async_trait;
use sqlx::PgPool;
use uuid::Uuid;
use chrono::Utc;

use crate::error::{ServiceError, ServiceResult};
use crate::models::{
    HomeworkSubmission, SubmissionStatus, CreateSubmissionRequest, UpdateSubmissionRequest,
    SubmissionListQuery, SubmissionListResponse,
};

pub struct SubmissionRepository {
    pool: PgPool,
}

impl SubmissionRepository {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }
}

#[async_trait]
pub trait SubmissionRepositoryTrait {
    async fn create(&self, homework_id: Uuid, student_id: Uuid, req: CreateSubmissionRequest, deadline: chrono::DateTime<Utc>) -> ServiceResult<HomeworkSubmission>;
    async fn find_by_id(&self, id: Uuid) -> ServiceResult<HomeworkSubmission>;
    async fn find_by_homework(&self, homework_id: Uuid, page: i32, page_size: i32) -> ServiceResult<SubmissionListResponse>;
    async fn find_by_student(&self, student_id: Uuid, page: i32, page_size: i32) -> ServiceResult<SubmissionListResponse>;
    async fn find_by_homework_and_student(&self, homework_id: Uuid, student_id: Uuid) -> ServiceResult<Option<HomeworkSubmission>>;
    async fn update(&self, id: Uuid, req: UpdateSubmissionRequest) -> ServiceResult<HomeworkSubmission>;
    async fn update_status(&self, id: Uuid, status: SubmissionStatus) -> ServiceResult<HomeworkSubmission>;
}

#[async_trait]
impl SubmissionRepositoryTrait for SubmissionRepository {
    async fn create(&self, homework_id: Uuid, student_id: Uuid, req: CreateSubmissionRequest, deadline: chrono::DateTime<Utc>) -> ServiceResult<HomeworkSubmission> {
        let id = Uuid::new_v4();
        let now = Utc::now();
        let is_late = now > deadline;

        let submission = sqlx::query_as!(
            HomeworkSubmission,
            r#"
            INSERT INTO homework_submissions (id, homework_id, student_id, content, attachments, submit_time, status, is_late, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, 'submitted', $7, $8)
            RETURNING id, homework_id, student_id, content, attachments, submit_time,
                      status as "status: SubmissionStatus", is_late, created_at, updated_at
            "#,
            id, homework_id, student_id, req.content, req.attachments as Option<Vec<String>>, now, is_late, now
        )
        .fetch_one(&self.pool)
        .await?;

        Ok(submission)
    }

    async fn find_by_id(&self, id: Uuid) -> ServiceResult<HomeworkSubmission> {
        let submission = sqlx::query_as!(
            HomeworkSubmission,
            r#"
            SELECT id, homework_id, student_id, content, attachments, submit_time,
                   status as "status: SubmissionStatus", is_late, created_at, updated_at
            FROM homework_submissions
            WHERE id = $1
            "#,
            id
        )
        .fetch_optional(&self.pool)
        .await?
        .ok_or_else(|| ServiceError::NotFound(format!("Submission with id {} not found", id)))?;

        Ok(submission)
    }

    async fn find_by_homework(&self, homework_id: Uuid, page: i32, page_size: i32) -> ServiceResult<SubmissionListResponse> {
        let page = page.max(1);
        let page_size = page_size.min(100).max(1);
        let offset = (page - 1) * page_size;

        let total: i64 = sqlx::query_scalar(
            "SELECT COUNT(*) FROM homework_submissions WHERE homework_id = $1"
        )
        .bind(homework_id)
        .fetch_one(&self.pool)
        .await?;

        let items: Vec<HomeworkSubmission> = sqlx::query_as(
            r#"
            SELECT id, homework_id, student_id, content, attachments, submit_time,
                   status as "status: SubmissionStatus", is_late, created_at, updated_at
            FROM homework_submissions
            WHERE homework_id = $1
            ORDER BY submit_time DESC
            LIMIT $2 OFFSET $3
            "#
        )
        .bind(homework_id)
        .bind(page_size as i64)
        .bind(offset as i64)
        .fetch_all(&self.pool)
        .await?;

        let total_pages = ((total as f64) / (page_size as f64)).ceil() as i32;

        Ok(SubmissionListResponse {
            items,
            total,
            page,
            page_size,
            total_pages,
        })
    }

    async fn find_by_student(&self, student_id: Uuid, page: i32, page_size: i32) -> ServiceResult<SubmissionListResponse> {
        let page = page.max(1);
        let page_size = page_size.min(100).max(1);
        let offset = (page - 1) * page_size;

        let total: i64 = sqlx::query_scalar(
            "SELECT COUNT(*) FROM homework_submissions WHERE student_id = $1"
        )
        .bind(student_id)
        .fetch_one(&self.pool)
        .await?;

        let items: Vec<HomeworkSubmission> = sqlx::query_as(
            r#"
            SELECT id, homework_id, student_id, content, attachments, submit_time,
                   status as "status: SubmissionStatus", is_late, created_at, updated_at
            FROM homework_submissions
            WHERE student_id = $1
            ORDER BY submit_time DESC
            LIMIT $2 OFFSET $3
            "#
        )
        .bind(student_id)
        .bind(page_size as i64)
        .bind(offset as i64)
        .fetch_all(&self.pool)
        .await?;

        let total_pages = ((total as f64) / (page_size as f64)).ceil() as i32;

        Ok(SubmissionListResponse {
            items,
            total,
            page,
            page_size,
            total_pages,
        })
    }

    async fn find_by_homework_and_student(&self, homework_id: Uuid, student_id: Uuid) -> ServiceResult<Option<HomeworkSubmission>> {
        let submission = sqlx::query_as!(
            HomeworkSubmission,
            r#"
            SELECT id, homework_id, student_id, content, attachments, submit_time,
                   status as "status: SubmissionStatus", is_late, created_at, updated_at
            FROM homework_submissions
            WHERE homework_id = $1 AND student_id = $2
            "#,
            homework_id, student_id
        )
        .fetch_optional(&self.pool)
        .await?;

        Ok(submission)
    }

    async fn update(&self, id: Uuid, req: UpdateSubmissionRequest) -> ServiceResult<HomeworkSubmission> {
        let now = Utc::now();

        let submission = sqlx::query_as!(
            HomeworkSubmission,
            r#"
            UPDATE homework_submissions
            SET content = COALESCE($1, content),
                attachments = COALESCE($2, attachments),
                updated_at = $3
            WHERE id = $4
            RETURNING id, homework_id, student_id, content, attachments, submit_time,
                      status as "status: SubmissionStatus", is_late, created_at, updated_at
            "#,
            req.content, req.attachments as Option<Vec<String>>, now, id
        )
        .fetch_optional(&self.pool)
        .await?
        .ok_or_else(|| ServiceError::NotFound(format!("Submission with id {} not found", id)))?;

        Ok(submission)
    }

    async fn update_status(&self, id: Uuid, status: SubmissionStatus) -> ServiceResult<HomeworkSubmission> {
        let now = Utc::now();

        let submission = sqlx::query_as!(
            HomeworkSubmission,
            r#"
            UPDATE homework_submissions
            SET status = $1, updated_at = $2
            WHERE id = $3
            RETURNING id, homework_id, student_id, content, attachments, submit_time,
                      status as "status: SubmissionStatus", is_late, created_at, updated_at
            "#,
            status as SubmissionStatus, now, id
        )
        .fetch_optional(&self.pool)
        .await?
        .ok_or_else(|| ServiceError::NotFound(format!("Submission with id {} not found", id)))?;

        Ok(submission)
    }
}
