use sqlx::postgres::{PgPool, PgPoolOptions};
use std::time::Duration;

use crate::config::DatabaseConfig;

pub type DbPool = PgPool;

pub async fn create_pool(config: &DatabaseConfig) -> Result<DbPool, sqlx::Error> {
    PgPoolOptions::new()
        .max_connections(config.max_connections)
        .acquire_timeout(Duration::from_secs(5))
        .connect(&config.url)
        .await
}

pub async fn run_migrations(pool: &DbPool) -> Result<(), sqlx::Error> {
    sqlx::query!(
        r#"
        CREATE TYPE homework_status AS ENUM ('draft', 'published', 'closed', 'archived');
        CREATE TYPE submission_status AS ENUM ('submitted', 'graded', 'returned');
        
        CREATE TABLE IF NOT EXISTS homework (
            id UUID PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            subject VARCHAR(50) NOT NULL,
            class_id UUID NOT NULL,
            teacher_id UUID NOT NULL,
            deadline TIMESTAMPTZ NOT NULL,
            status homework_status NOT NULL DEFAULT 'draft',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ
        );
        
        CREATE TABLE IF NOT EXISTS homework_submissions (
            id UUID PRIMARY KEY,
            homework_id UUID NOT NULL REFERENCES homework(id) ON DELETE CASCADE,
            student_id UUID NOT NULL,
            content TEXT,
            attachments TEXT[],
            submit_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            status submission_status NOT NULL DEFAULT 'submitted',
            is_late BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ
        );
        
        CREATE TABLE IF NOT EXISTS homework_grades (
            id UUID PRIMARY KEY,
            submission_id UUID NOT NULL REFERENCES homework_submissions(id) ON DELETE CASCADE,
            score DECIMAL(5,2) NOT NULL,
            max_score DECIMAL(5,2) NOT NULL,
            comment TEXT,
            graded_by UUID NOT NULL,
            graded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_homework_class_id ON homework(class_id);
        CREATE INDEX IF NOT EXISTS idx_homework_teacher_id ON homework(teacher_id);
        CREATE INDEX IF NOT EXISTS idx_homework_status ON homework(status);
        CREATE INDEX IF NOT EXISTS idx_submission_homework_id ON homework_submissions(homework_id);
        CREATE INDEX IF NOT EXISTS idx_submission_student_id ON homework_submissions(student_id);
        CREATE INDEX IF NOT EXISTS idx_grade_submission_id ON homework_grades(submission_id);
        "#
    )
    .execute(pool)
    .await?;

    Ok(())
}
