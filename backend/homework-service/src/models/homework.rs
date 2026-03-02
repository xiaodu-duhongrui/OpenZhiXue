use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;
use validator::Validate;

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Homework {
    pub id: Uuid,
    pub title: String,
    pub description: Option<String>,
    pub subject: String,
    pub class_id: Uuid,
    pub teacher_id: Uuid,
    pub deadline: DateTime<Utc>,
    pub status: HomeworkStatus,
    pub created_at: DateTime<Utc>,
    pub updated_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "homework_status", rename_all = "lowercase")]
pub enum HomeworkStatus {
    Draft,
    Published,
    Closed,
    Archived,
}

impl Default for HomeworkStatus {
    fn default() -> Self {
        Self::Draft
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct CreateHomeworkRequest {
    #[validate(length(min = 1, max = 200))]
    pub title: String,
    pub description: Option<String>,
    #[validate(length(min = 1, max = 50))]
    pub subject: String,
    pub class_id: Uuid,
    pub teacher_id: Uuid,
    pub deadline: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct UpdateHomeworkRequest {
    #[validate(length(min = 1, max = 200))]
    pub title: Option<String>,
    pub description: Option<String>,
    #[validate(length(min = 1, max = 50))]
    pub subject: Option<String>,
    pub deadline: Option<DateTime<Utc>>,
    pub status: Option<HomeworkStatus>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HomeworkListQuery {
    pub class_id: Option<Uuid>,
    pub teacher_id: Option<Uuid>,
    pub subject: Option<String>,
    pub status: Option<HomeworkStatus>,
    pub page: Option<i32>,
    pub page_size: Option<i32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HomeworkListResponse {
    pub items: Vec<Homework>,
    pub total: i64,
    pub page: i32,
    pub page_size: i32,
    pub total_pages: i32,
}

impl Homework {
    pub fn new(
        title: String,
        description: Option<String>,
        subject: String,
        class_id: Uuid,
        teacher_id: Uuid,
        deadline: DateTime<Utc>,
    ) -> Self {
        Self {
            id: Uuid::new_v4(),
            title,
            description,
            subject,
            class_id,
            teacher_id,
            deadline,
            status: HomeworkStatus::Draft,
            created_at: Utc::now(),
            updated_at: None,
        }
    }

    pub fn publish(&mut self) {
        self.status = HomeworkStatus::Published;
        self.updated_at = Some(Utc::now());
    }

    pub fn close(&mut self) {
        self.status = HomeworkStatus::Closed;
        self.updated_at = Some(Utc::now());
    }

    pub fn is_expired(&self) -> bool {
        Utc::now() > self.deadline
    }
}
