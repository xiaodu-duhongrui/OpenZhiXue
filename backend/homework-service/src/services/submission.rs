use uuid::Uuid;
use std::sync::Arc;

use crate::error::{ServiceError, ServiceResult};
use crate::models::{
    HomeworkSubmission, SubmissionStatus, CreateSubmissionRequest, UpdateSubmissionRequest,
    SubmissionListQuery, SubmissionListResponse,
};
use crate::repository::{HomeworkRepository, HomeworkRepositoryTrait, SubmissionRepository, SubmissionRepositoryTrait};

pub struct SubmissionService {
    homework_repository: Arc<HomeworkRepository>,
    submission_repository: Arc<SubmissionRepository>,
}

impl SubmissionService {
    pub fn new(
        homework_repository: Arc<HomeworkRepository>,
        submission_repository: Arc<SubmissionRepository>,
    ) -> Self {
        Self {
            homework_repository,
            submission_repository,
        }
    }

    pub async fn submit_homework(&self, homework_id: Uuid, student_id: Uuid, req: CreateSubmissionRequest) -> ServiceResult<HomeworkSubmission> {
        let homework = self.homework_repository.find_by_id(homework_id).await?;

        if homework.status != HomeworkStatus::Published {
            return Err(ServiceError::BadRequest("Homework is not available for submission".to_string()));
        }

        let existing = self.submission_repository.find_by_homework_and_student(homework_id, student_id).await?;
        if existing.is_some() {
            return Err(ServiceError::BadRequest("You have already submitted this homework".to_string()));
        }

        self.submission_repository.create(homework_id, student_id, req, homework.deadline).await
    }

    pub async fn get_submission(&self, id: Uuid) -> ServiceResult<HomeworkSubmission> {
        self.submission_repository.find_by_id(id).await
    }

    pub async fn list_submissions_by_homework(&self, homework_id: Uuid, page: i32, page_size: i32) -> ServiceResult<SubmissionListResponse> {
        self.submission_repository.find_by_homework(homework_id, page, page_size).await
    }

    pub async fn list_submissions_by_student(&self, student_id: Uuid, page: i32, page_size: i32) -> ServiceResult<SubmissionListResponse> {
        self.submission_repository.find_by_student(student_id, page, page_size).await
    }

    pub async fn update_submission(&self, id: Uuid, student_id: Uuid, req: UpdateSubmissionRequest) -> ServiceResult<HomeworkSubmission> {
        let submission = self.submission_repository.find_by_id(id).await?;

        if submission.student_id != student_id {
            return Err(ServiceError::Forbidden("You can only update your own submission".to_string()));
        }

        if submission.status == SubmissionStatus::Graded {
            return Err(ServiceError::BadRequest("Cannot update a graded submission".to_string()));
        }

        self.submission_repository.update(id, req).await
    }

    pub async fn resubmit_submission(&self, id: Uuid, student_id: Uuid, req: CreateSubmissionRequest) -> ServiceResult<HomeworkSubmission> {
        let submission = self.submission_repository.find_by_id(id).await?;

        if submission.student_id != student_id {
            return Err(ServiceError::Forbidden("You can only resubmit your own submission".to_string()));
        }

        let homework = self.homework_repository.find_by_id(submission.homework_id).await?;
        
        if homework.is_expired() {
            return Err(ServiceError::BadRequest("Cannot resubmit after deadline".to_string()));
        }

        let update_req = UpdateSubmissionRequest {
            content: req.content,
            attachments: req.attachments,
        };

        self.submission_repository.update(id, update_req).await
    }
}
