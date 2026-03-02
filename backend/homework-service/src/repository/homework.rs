use async_trait::async_trait;
use sqlx::PgPool;
use uuid::Uuid;
use chrono::Utc;

use crate::error::{ServiceError, ServiceResult};
use crate::models::{
    Homework, HomeworkStatus, CreateHomeworkRequest, UpdateHomeworkRequest,
    HomeworkListQuery, HomeworkListResponse,
};

pub struct HomeworkRepository {
    pool: PgPool,
}

impl HomeworkRepository {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }
}

#[async_trait]
pub trait HomeworkRepositoryTrait {
    async fn create(&self, req: CreateHomeworkRequest) -> ServiceResult<Homework>;
    async fn find_by_id(&self, id: Uuid) -> ServiceResult<Homework>;
    async fn find_all(&self, query: HomeworkListQuery) -> ServiceResult<HomeworkListResponse>;
    async fn find_by_class(&self, class_id: Uuid, page: i32, page_size: i32) -> ServiceResult<HomeworkListResponse>;
    async fn update(&self, id: Uuid, req: UpdateHomeworkRequest) -> ServiceResult<Homework>;
    async fn delete(&self, id: Uuid) -> ServiceResult<()>;
    async fn update_status(&self, id: Uuid, status: HomeworkStatus) -> ServiceResult<Homework>;
}

#[async_trait]
impl HomeworkRepositoryTrait for HomeworkRepository {
    async fn create(&self, req: CreateHomeworkRequest) -> ServiceResult<Homework> {
        let id = Uuid::new_v4();
        let now = Utc::now();
        
        let homework = sqlx::query_as!(
            Homework,
            r#"
            INSERT INTO homework (id, title, description, subject, class_id, teacher_id, deadline, status, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, 'draft', $8)
            RETURNING id, title, description, subject, class_id, teacher_id, deadline,
                      status as "status: HomeworkStatus", created_at, updated_at
            "#,
            id, req.title, req.description, req.subject, req.class_id, req.teacher_id, req.deadline, now
        )
        .fetch_one(&self.pool)
        .await?;

        Ok(homework)
    }

    async fn find_by_id(&self, id: Uuid) -> ServiceResult<Homework> {
        let homework = sqlx::query_as!(
            Homework,
            r#"
            SELECT id, title, description, subject, class_id, teacher_id, deadline,
                   status as "status: HomeworkStatus", created_at, updated_at
            FROM homework
            WHERE id = $1
            "#,
            id
        )
        .fetch_optional(&self.pool)
        .await?
        .ok_or_else(|| ServiceError::NotFound(format!("Homework with id {} not found", id)))?;

        Ok(homework)
    }

    async fn find_all(&self, query: HomeworkListQuery) -> ServiceResult<HomeworkListResponse> {
        let page = query.page.unwrap_or(1).max(1);
        let page_size = query.page_size.unwrap_or(10).min(100).max(1);
        let offset = (page - 1) * page_size;

        let mut conditions = Vec::new();
        let mut param_count = 1;

        if let Some(class_id) = query.class_id {
            conditions.push(format!("class_id = ${}", param_count));
            param_count += 1;
        }
        if let Some(teacher_id) = query.teacher_id {
            conditions.push(format!("teacher_id = ${}", param_count));
            param_count += 1;
        }
        if let Some(ref subject) = query.subject {
            conditions.push(format!("subject = ${}", param_count));
            param_count += 1;
        }
        if let Some(ref status) = query.status {
            conditions.push(format!("status = ${}", param_count));
            param_count += 1;
        }

        let where_clause = if conditions.is_empty() {
            String::new()
        } else {
            format!("WHERE {}", conditions.join(" AND "))
        };

        let count_query = format!("SELECT COUNT(*) FROM homework {}", where_clause);
        let total: i64 = sqlx::query_scalar(&count_query)
            .fetch_one(&self.pool)
            .await?;

        let select_query = format!(
            r#"
            SELECT id, title, description, subject, class_id, teacher_id, deadline,
                   status as "status: HomeworkStatus", created_at, updated_at
            FROM homework
            {}
            ORDER BY created_at DESC
            LIMIT ${} OFFSET ${}
            "#,
            where_clause, param_count, param_count + 1
        );

        let items: Vec<Homework> = sqlx::query_as(&select_query)
            .bind(page_size as i64)
            .bind(offset as i64)
            .fetch_all(&self.pool)
            .await?;

        let total_pages = ((total as f64) / (page_size as f64)).ceil() as i32;

        Ok(HomeworkListResponse {
            items,
            total,
            page,
            page_size,
            total_pages,
        })
    }

    async fn find_by_class(&self, class_id: Uuid, page: i32, page_size: i32) -> ServiceResult<HomeworkListResponse> {
        let page = page.max(1);
        let page_size = page_size.min(100).max(1);
        let offset = (page - 1) * page_size;

        let total: i64 = sqlx::query_scalar(
            "SELECT COUNT(*) FROM homework WHERE class_id = $1"
        )
        .bind(class_id)
        .fetch_one(&self.pool)
        .await?;

        let items: Vec<Homework> = sqlx::query_as(
            r#"
            SELECT id, title, description, subject, class_id, teacher_id, deadline,
                   status as "status: HomeworkStatus", created_at, updated_at
            FROM homework
            WHERE class_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
            "#
        )
        .bind(class_id)
        .bind(page_size as i64)
        .bind(offset as i64)
        .fetch_all(&self.pool)
        .await?;

        let total_pages = ((total as f64) / (page_size as f64)).ceil() as i32;

        Ok(HomeworkListResponse {
            items,
            total,
            page,
            page_size,
            total_pages,
        })
    }

    async fn update(&self, id: Uuid, req: UpdateHomeworkRequest) -> ServiceResult<Homework> {
        let now = Utc::now();
        
        let homework = sqlx::query_as!(
            Homework,
            r#"
            UPDATE homework
            SET title = COALESCE($1, title),
                description = COALESCE($2, description),
                subject = COALESCE($3, subject),
                deadline = COALESCE($4, deadline),
                status = COALESCE($5, status),
                updated_at = $6
            WHERE id = $7
            RETURNING id, title, description, subject, class_id, teacher_id, deadline,
                      status as "status: HomeworkStatus", created_at, updated_at
            "#,
            req.title, req.description, req.subject, req.deadline, req.status as Option<HomeworkStatus>, now, id
        )
        .fetch_optional(&self.pool)
        .await?
        .ok_or_else(|| ServiceError::NotFound(format!("Homework with id {} not found", id)))?;

        Ok(homework)
    }

    async fn delete(&self, id: Uuid) -> ServiceResult<()> {
        let result = sqlx::query("DELETE FROM homework WHERE id = $1")
            .bind(id)
            .execute(&self.pool)
            .await?;

        if result.rows_affected() == 0 {
            return Err(ServiceError::NotFound(format!("Homework with id {} not found", id)));
        }

        Ok(())
    }

    async fn update_status(&self, id: Uuid, status: HomeworkStatus) -> ServiceResult<Homework> {
        let now = Utc::now();
        
        let homework = sqlx::query_as!(
            Homework,
            r#"
            UPDATE homework
            SET status = $1, updated_at = $2
            WHERE id = $3
            RETURNING id, title, description, subject, class_id, teacher_id, deadline,
                      status as "status: HomeworkStatus", created_at, updated_at
            "#,
            status as HomeworkStatus, now, id
        )
        .fetch_optional(&self.pool)
        .await?
        .ok_or_else(|| ServiceError::NotFound(format!("Homework with id {} not found", id)))?;

        Ok(homework)
    }
}
