use actix_web::{http::StatusCode, HttpResponse};
use crate::error::{ServiceError, ServiceResult};

#[test]
fn test_service_error_not_found() {
    let error = ServiceError::NotFound("Resource not found".to_string());
    
    assert_eq!(error.status_code(), StatusCode::NOT_FOUND);
    assert!(error.to_string().contains("Not Found"));
}

#[test]
fn test_service_error_bad_request() {
    let error = ServiceError::BadRequest("Invalid input".to_string());
    
    assert_eq!(error.status_code(), StatusCode::BAD_REQUEST);
    assert!(error.to_string().contains("Bad Request"));
}

#[test]
fn test_service_error_unauthorized() {
    let error = ServiceError::Unauthorized("Not authenticated".to_string());
    
    assert_eq!(error.status_code(), StatusCode::UNAUTHORIZED);
    assert!(error.to_string().contains("Unauthorized"));
}

#[test]
fn test_service_error_forbidden() {
    let error = ServiceError::Forbidden("Access denied".to_string());
    
    assert_eq!(error.status_code(), StatusCode::FORBIDDEN);
    assert!(error.to_string().contains("Forbidden"));
}

#[test]
fn test_service_error_internal() {
    let error = ServiceError::InternalError("Server error".to_string());
    
    assert_eq!(error.status_code(), StatusCode::INTERNAL_SERVER_ERROR);
    assert!(error.to_string().contains("Internal Error"));
}

#[test]
fn test_service_error_database() {
    let error = ServiceError::DatabaseError("Connection failed".to_string());
    
    assert_eq!(error.status_code(), StatusCode::INTERNAL_SERVER_ERROR);
    assert!(error.to_string().contains("Database Error"));
}

#[test]
fn test_service_error_validation() {
    let error = ServiceError::ValidationError("Invalid field".to_string());
    
    assert_eq!(error.status_code(), StatusCode::BAD_REQUEST);
    assert!(error.to_string().contains("Validation Error"));
}

#[test]
fn test_service_error_error_response() {
    let error = ServiceError::NotFound("Test resource".to_string());
    let response = error.error_response();
    
    assert_eq!(response.status(), StatusCode::NOT_FOUND);
}

#[test]
fn test_service_result_ok() {
    let result: ServiceResult<i32> = Ok(42);
    assert!(result.is_ok());
    assert_eq!(result.unwrap(), 42);
}

#[test]
fn test_service_result_err() {
    let result: ServiceResult<i32> = Err(ServiceError::NotFound("test".to_string()));
    assert!(result.is_err());
}

#[test]
fn test_from_sqlx_error_row_not_found() {
    let sqlx_error = sqlx::Error::RowNotFound;
    let service_error: ServiceError = sqlx_error.into();
    
    assert!(matches!(service_error, ServiceError::NotFound(_)));
}
