use std::sync::Arc;
use uuid::Uuid;
use chrono::{Duration, Utc};
use mockall::predicate::*;
use mockall::mock;

use crate::models::{Homework, HomeworkStatus, CreateHomeworkRequest, UpdateHomeworkRequest, HomeworkListQuery, HomeworkListResponse};
use crate::services::HomeworkService;
use crate::error::ServiceResult;

mock! {
    pub HomeworkRepository {}
    
    impl HomeworkRepositoryTrait for HomeworkRepository {
        async fn create(&self, req: CreateHomeworkRequest) -> ServiceResult<Homework>;
        async fn find_by_id(&self, id: Uuid) -> ServiceResult<Homework>;
        async fn find_all(&self, query: HomeworkListQuery) -> ServiceResult<HomeworkListResponse>;
        async fn find_by_class(&self, class_id: Uuid, page: i32, page_size: i32) -> ServiceResult<HomeworkListResponse>;
        async fn update(&self, id: Uuid, req: UpdateHomeworkRequest) -> ServiceResult<Homework>;
        async fn delete(&self, id: Uuid) -> ServiceResult<()>;
        async fn update_status(&self, id: Uuid, status: HomeworkStatus) -> ServiceResult<Homework>;
    }
}

fn create_test_homework() -> Homework {
    Homework {
        id: Uuid::new_v4(),
        title: "Test Homework".to_string(),
        description: Some("Test Description".to_string()),
        subject: "Math".to_string(),
        class_id: Uuid::new_v4(),
        teacher_id: Uuid::new_v4(),
        deadline: Utc::now() + Duration::days(7),
        status: HomeworkStatus::Draft,
        created_at: Utc::now(),
        updated_at: None,
    }
}

fn create_test_request() -> CreateHomeworkRequest {
    CreateHomeworkRequest {
        title: "Test Homework".to_string(),
        description: Some("Test Description".to_string()),
        subject: "Math".to_string(),
        class_id: Uuid::new_v4(),
        teacher_id: Uuid::new_v4(),
        deadline: Utc::now() + Duration::days(7),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_service_new() {
        let repo = Arc::new(MockHomeworkRepository::new());
        let service = HomeworkService::new(repo);
        
        assert!(true);
    }
}
