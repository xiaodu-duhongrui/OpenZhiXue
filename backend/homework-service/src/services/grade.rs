use uuid::Uuid;
use std::sync::Arc;

use crate::error::{ServiceError, ServiceResult};
use crate::models::{
    HomeworkGrade, CreateGradeRequest, UpdateGradeRequest, BatchGradeRequest,
    HomeworkStatistics,
};
use crate::repository::{GradeRepository, GradeRepositoryTrait, SubmissionRepository, SubmissionRepositoryTrait};

pub struct GradeService {
    grade_repository: Arc<GradeRepository>,
    submission_repository: Arc<SubmissionRepository>,
}

impl GradeService {
    pub fn new(
        grade_repository: Arc<GradeRepository>,
        submission_repository: Arc<SubmissionRepository>,
    ) -> Self {
        Self {
            grade_repository,
            submission_repository,
        }
    }

    pub async fn grade_submission(&self, submission_id: Uuid, graded_by: Uuid, req: CreateGradeRequest) -> ServiceResult<HomeworkGrade> {
        if req.score > req.max_score {
            return Err(ServiceError::BadRequest("Score cannot be greater than max score".to_string()));
        }

        let existing = self.grade_repository.find_by_submission(submission_id).await?;
        if existing.is_some() {
            return Err(ServiceError::BadRequest("Submission already graded".to_string()));
        }

        self.grade_repository.create(submission_id, graded_by, req).await
    }

    pub async fn get_grade(&self, id: Uuid) -> ServiceResult<HomeworkGrade> {
        self.grade_repository.find_by_id(id).await
    }

    pub async fn get_grade_by_submission(&self, submission_id: Uuid) -> ServiceResult<Option<HomeworkGrade>> {
        self.grade_repository.find_by_submission(submission_id).await
    }

    pub async fn update_grade(&self, id: Uuid, graded_by: Uuid, req: UpdateGradeRequest) -> ServiceResult<HomeworkGrade> {
        let grade = self.grade_repository.find_by_id(id).await?;

        if grade.graded_by != graded_by {
            return Err(ServiceError::Forbidden("You can only update grades you created".to_string()));
        }

        let new_score = req.score.unwrap_or(grade.score);
        let new_max_score = req.max_score.unwrap_or(grade.max_score);

        if new_score > new_max_score {
            return Err(ServiceError::BadRequest("Score cannot be greater than max score".to_string()));
        }

        self.grade_repository.update(id, req).await
    }

    pub async fn batch_grade(&self, graded_by: Uuid, req: BatchGradeRequest) -> ServiceResult<Vec<HomeworkGrade>> {
        for item in &req.grades {
            if item.score > item.max_score {
                return Err(ServiceError::BadRequest(
                    format!("Score cannot be greater than max score for submission {}", item.submission_id)
                ));
            }

            let existing = self.grade_repository.find_by_submission(item.submission_id).await?;
            if existing.is_some() {
                return Err(ServiceError::BadRequest(
                    format!("Submission {} already graded", item.submission_id)
                ));
            }
        }

        self.grade_repository.batch_create(graded_by, req).await
    }

    pub async fn get_homework_statistics(&self, homework_id: Uuid) -> ServiceResult<HomeworkStatistics> {
        self.grade_repository.get_statistics(homework_id).await
    }

    pub async fn return_submission(&self, submission_id: Uuid, teacher_id: Uuid) -> ServiceResult<()> {
        let grade = self.grade_repository.find_by_submission(submission_id).await?;

        if let Some(grade) = grade {
            if grade.graded_by != teacher_id {
                return Err(ServiceError::Forbidden("You can only return submissions you graded".to_string()));
            }
        }

        self.submission_repository.update_status(submission_id, crate::models::SubmissionStatus::Returned).await?;
        Ok(())
    }
}
