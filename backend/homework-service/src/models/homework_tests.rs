use chrono::{Duration, Utc};
use uuid::Uuid;

use crate::models::{Homework, HomeworkStatus, CreateHomeworkRequest, UpdateHomeworkRequest};

#[test]
fn test_homework_new() {
    let title = "Test Homework".to_string();
    let description = Some("Test Description".to_string());
    let subject = "Math".to_string();
    let class_id = Uuid::new_v4();
    let teacher_id = Uuid::new_v4();
    let deadline = Utc::now() + Duration::days(7);

    let homework = Homework::new(
        title.clone(),
        description.clone(),
        subject.clone(),
        class_id,
        teacher_id,
        deadline,
    );

    assert_eq!(homework.title, title);
    assert_eq!(homework.description, description);
    assert_eq!(homework.subject, subject);
    assert_eq!(homework.class_id, class_id);
    assert_eq!(homework.teacher_id, teacher_id);
    assert_eq!(homework.deadline, deadline);
    assert_eq!(homework.status, HomeworkStatus::Draft);
    assert!(homework.updated_at.is_none());
}

#[test]
fn test_homework_publish() {
    let mut homework = create_test_homework();
    
    assert_eq!(homework.status, HomeworkStatus::Draft);
    
    homework.publish();
    
    assert_eq!(homework.status, HomeworkStatus::Published);
    assert!(homework.updated_at.is_some());
}

#[test]
fn test_homework_close() {
    let mut homework = create_test_homework();
    
    homework.close();
    
    assert_eq!(homework.status, HomeworkStatus::Closed);
    assert!(homework.updated_at.is_some());
}

#[test]
fn test_homework_is_expired_false() {
    let homework = Homework::new(
        "Test".to_string(),
        None,
        "Math".to_string(),
        Uuid::new_v4(),
        Uuid::new_v4(),
        Utc::now() + Duration::days(7),
    );
    
    assert!(!homework.is_expired());
}

#[test]
fn test_homework_is_expired_true() {
    let homework = Homework::new(
        "Test".to_string(),
        None,
        "Math".to_string(),
        Uuid::new_v4(),
        Uuid::new_v4(),
        Utc::now() - Duration::hours(1),
    );
    
    assert!(homework.is_expired());
}

#[test]
fn test_homework_status_default() {
    let status = HomeworkStatus::default();
    assert!(matches!(status, HomeworkStatus::Draft));
}

#[test]
fn test_create_homework_request_validation_valid() {
    let request = CreateHomeworkRequest {
        title: "Valid Title".to_string(),
        description: Some("Description".to_string()),
        subject: "Math".to_string(),
        class_id: Uuid::new_v4(),
        teacher_id: Uuid::new_v4(),
        deadline: Utc::now() + Duration::days(7),
    };
    
    assert!(request.validate().is_ok());
}

#[test]
fn test_create_homework_request_validation_empty_title() {
    let request = CreateHomeworkRequest {
        title: "".to_string(),
        description: None,
        subject: "Math".to_string(),
        class_id: Uuid::new_v4(),
        teacher_id: Uuid::new_v4(),
        deadline: Utc::now() + Duration::days(7),
    };
    
    assert!(request.validate().is_err());
}

#[test]
fn test_create_homework_request_validation_long_title() {
    let long_title = "a".repeat(201);
    let request = CreateHomeworkRequest {
        title: long_title,
        description: None,
        subject: "Math".to_string(),
        class_id: Uuid::new_v4(),
        teacher_id: Uuid::new_v4(),
        deadline: Utc::now() + Duration::days(7),
    };
    
    assert!(request.validate().is_err());
}

#[test]
fn test_create_homework_request_validation_empty_subject() {
    let request = CreateHomeworkRequest {
        title: "Valid Title".to_string(),
        description: None,
        subject: "".to_string(),
        class_id: Uuid::new_v4(),
        teacher_id: Uuid::new_v4(),
        deadline: Utc::now() + Duration::days(7),
    };
    
    assert!(request.validate().is_err());
}

#[test]
fn test_update_homework_request_validation_valid() {
    let request = UpdateHomeworkRequest {
        title: Some("New Title".to_string()),
        description: Some("New Description".to_string()),
        subject: Some("Physics".to_string()),
        deadline: Some(Utc::now() + Duration::days(14)),
        status: Some(HomeworkStatus::Published),
    };
    
    assert!(request.validate().is_ok());
}

#[test]
fn test_update_homework_request_validation_empty() {
    let request = UpdateHomeworkRequest {
        title: None,
        description: None,
        subject: None,
        deadline: None,
        status: None,
    };
    
    assert!(request.validate().is_ok());
}

#[test]
fn test_update_homework_request_validation_invalid_title() {
    let request = UpdateHomeworkRequest {
        title: Some("".to_string()),
        description: None,
        subject: None,
        deadline: None,
        status: None,
    };
    
    assert!(request.validate().is_err());
}

fn create_test_homework() -> Homework {
    Homework::new(
        "Test Homework".to_string(),
        Some("Test Description".to_string()),
        "Math".to_string(),
        Uuid::new_v4(),
        Uuid::new_v4(),
        Utc::now() + Duration::days(7),
    )
}
