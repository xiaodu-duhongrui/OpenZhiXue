use uuid::Uuid;
use std::sync::Arc;

use crate::error::ServiceResult;
use crate::models::{
    Homework, HomeworkStatus, CreateHomeworkRequest, UpdateHomeworkRequest,
    HomeworkListQuery, HomeworkListResponse,
};
use crate::repository::{HomeworkRepository, HomeworkRepositoryTrait};

pub struct HomeworkService {
    repository: Arc<HomeworkRepository>,
}

impl HomeworkService {
    pub fn new(repository: Arc<HomeworkRepository>) -> Self {
        Self { repository }
    }

    pub async fn create_homework(&self, req: CreateHomeworkRequest) -> ServiceResult<Homework> {
        self.repository.create(req).await
    }

    pub async fn get_homework(&self, id: Uuid) -> ServiceResult<Homework> {
        self.repository.find_by_id(id).await
    }

    pub async fn list_homework(&self, query: HomeworkListQuery) -> ServiceResult<HomeworkListResponse> {
        self.repository.find_all(query).await
    }

    pub async fn list_homework_by_class(&self, class_id: Uuid, page: i32, page_size: i32) -> ServiceResult<HomeworkListResponse> {
        self.repository.find_by_class(class_id, page, page_size).await
    }

    pub async fn update_homework(&self, id: Uuid, req: UpdateHomeworkRequest) -> ServiceResult<Homework> {
        self.repository.update(id, req).await
    }

    pub async fn delete_homework(&self, id: Uuid) -> ServiceResult<()> {
        self.repository.delete(id).await
    }

    pub async fn publish_homework(&self, id: Uuid) -> ServiceResult<Homework> {
        self.repository.update_status(id, HomeworkStatus::Published).await
    }

    pub async fn close_homework(&self, id: Uuid) -> ServiceResult<Homework> {
        self.repository.update_status(id, HomeworkStatus::Closed).await
    }

    pub async fn archive_homework(&self, id: Uuid) -> ServiceResult<Homework> {
        self.repository.update_status(id, HomeworkStatus::Archived).await
    }
}
