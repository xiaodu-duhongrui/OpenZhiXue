use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;
use validator::Validate;

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct HomeworkGrade {
    pub id: Uuid,
    pub submission_id: Uuid,
    pub score: f64,
    pub max_score: f64,
    pub comment: Option<String>,
    pub graded_by: Uuid,
    pub graded_at: DateTime<Utc>,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct CreateGradeRequest {
    #[validate(range(min = 0.0))]
    pub score: f64,
    #[validate(range(min = 0.0))]
    pub max_score: f64,
    pub comment: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct UpdateGradeRequest {
    #[validate(range(min = 0.0))]
    pub score: Option<f64>,
    #[validate(range(min = 0.0))]
    pub max_score: Option<f64>,
    pub comment: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct BatchGradeRequest {
    pub grades: Vec<BatchGradeItem>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct BatchGradeItem {
    pub submission_id: Uuid,
    #[validate(range(min = 0.0))]
    pub score: f64,
    #[validate(range(min = 0.0))]
    pub max_score: f64,
    pub comment: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HomeworkStatistics {
    pub homework_id: Uuid,
    pub total_students: i64,
    pub submitted_count: i64,
    pub graded_count: i64,
    pub average_score: Option<f64>,
    pub highest_score: Option<f64>,
    pub lowest_score: Option<f64>,
    pub submission_rate: f64,
    pub score_distribution: ScoreDistribution,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScoreDistribution {
    pub excellent: i64,
    pub good: i64,
    pub average: i64,
    pub pass: i64,
    pub fail: i64,
}

impl HomeworkGrade {
    pub fn new(
        submission_id: Uuid,
        score: f64,
        max_score: f64,
        comment: Option<String>,
        graded_by: Uuid,
    ) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            submission_id,
            score,
            max_score,
            comment,
            graded_by,
            graded_at: now,
            created_at: now,
        }
    }

    pub fn percentage(&self) -> f64 {
        if self.max_score > 0.0 {
            (self.score / self.max_score) * 100.0
        } else {
            0.0
        }
    }
}

impl ScoreDistribution {
    pub fn new() -> Self {
        Self {
            excellent: 0,
            good: 0,
            average: 0,
            pass: 0,
            fail: 0,
        }
    }

    pub fn add_score(&mut self, percentage: f64) {
        if percentage >= 90.0 {
            self.excellent += 1;
        } else if percentage >= 80.0 {
            self.good += 1;
        } else if percentage >= 70.0 {
            self.average += 1;
        } else if percentage >= 60.0 {
            self.pass += 1;
        } else {
            self.fail += 1;
        }
    }
}
