use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;
use validator::Validate;

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct HomeworkSubmission {
    pub id: Uuid,
    pub homework_id: Uuid,
    pub student_id: Uuid,
    pub content: Option<String>,
    pub attachments: Option<Vec<String>>,
    pub submit_time: DateTime<Utc>,
    pub status: SubmissionStatus,
    pub is_late: bool,
    pub created_at: DateTime<Utc>,
    pub updated_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "submission_status", rename_all = "lowercase")]
pub enum SubmissionStatus {
    Submitted,
    Graded,
    Returned,
}

impl Default for SubmissionStatus {
    fn default() -> Self {
        Self::Submitted
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct CreateSubmissionRequest {
    pub content: Option<String>,
    pub attachments: Option<Vec<String>>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct UpdateSubmissionRequest {
    pub content: Option<String>,
    pub attachments: Option<Vec<String>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SubmissionListQuery {
    pub homework_id: Option<Uuid>,
    pub student_id: Option<Uuid>,
    pub status: Option<SubmissionStatus>,
    pub page: Option<i32>,
    pub page_size: Option<i32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SubmissionListResponse {
    pub items: Vec<HomeworkSubmission>,
    pub total: i64,
    pub page: i32,
    pub page_size: i32,
    pub total_pages: i32,
}

impl HomeworkSubmission {
    pub fn new(
        homework_id: Uuid,
        student_id: Uuid,
        content: Option<String>,
        attachments: Option<Vec<String>>,
        deadline: DateTime<Utc>,
    ) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            homework_id,
            student_id,
            content,
            attachments,
            submit_time: now,
            status: SubmissionStatus::Submitted,
            is_late: now > deadline,
            created_at: now,
            updated_at: None,
        }
    }

    pub fn mark_graded(&mut self) {
        self.status = SubmissionStatus::Graded;
        self.updated_at = Some(Utc::now());
    }

    pub fn mark_returned(&mut self) {
        self.status = SubmissionStatus::Returned;
        self.updated_at = Some(Utc::now());
    }
}
