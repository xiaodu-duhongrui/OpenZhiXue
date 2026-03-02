use actix_web::{http::StatusCode, HttpResponse, ResponseError};
use std::fmt;

#[derive(Debug)]
pub enum ServiceError {
    NotFound(String),
    BadRequest(String),
    Unauthorized(String),
    Forbidden(String),
    InternalError(String),
    DatabaseError(String),
    ValidationError(String),
}

impl fmt::Display for ServiceError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ServiceError::NotFound(msg) => write!(f, "Not Found: {}", msg),
            ServiceError::BadRequest(msg) => write!(f, "Bad Request: {}", msg),
            ServiceError::Unauthorized(msg) => write!(f, "Unauthorized: {}", msg),
            ServiceError::Forbidden(msg) => write!(f, "Forbidden: {}", msg),
            ServiceError::InternalError(msg) => write!(f, "Internal Error: {}", msg),
            ServiceError::DatabaseError(msg) => write!(f, "Database Error: {}", msg),
            ServiceError::ValidationError(msg) => write!(f, "Validation Error: {}", msg),
        }
    }
}

impl ResponseError for ServiceError {
    fn error_response(&self) -> HttpResponse {
        let status_code = self.status_code();
        let error_message = self.to_string();

        HttpResponse::build(status_code).json(serde_json::json!({
            "error": {
                "code": status_code.as_u16(),
                "message": error_message
            }
        }))
    }

    fn status_code(&self) -> StatusCode {
        match self {
            ServiceError::NotFound(_) => StatusCode::NOT_FOUND,
            ServiceError::BadRequest(_) => StatusCode::BAD_REQUEST,
            ServiceError::Unauthorized(_) => StatusCode::UNAUTHORIZED,
            ServiceError::Forbidden(_) => StatusCode::FORBIDDEN,
            ServiceError::InternalError(_) => StatusCode::INTERNAL_SERVER_ERROR,
            ServiceError::DatabaseError(_) => StatusCode::INTERNAL_SERVER_ERROR,
            ServiceError::ValidationError(_) => StatusCode::BAD_REQUEST,
        }
    }
}

impl From<sqlx::Error> for ServiceError {
    fn from(err: sqlx::Error) -> Self {
        match err {
            sqlx::Error::RowNotFound => ServiceError::NotFound("Record not found".to_string()),
            _ => ServiceError::DatabaseError(err.to_string()),
        }
    }
}

impl From<validator::ValidationErrors> for ServiceError {
    fn from(err: validator::ValidationErrors) -> Self {
        ServiceError::ValidationError(err.to_string())
    }
}

pub type ServiceResult<T> = Result<T, ServiceError>;
