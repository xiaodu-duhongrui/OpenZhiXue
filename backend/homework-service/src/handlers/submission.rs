use actix_web::{web, HttpResponse};
use serde::Deserialize;
use std::sync::Arc;
use uuid::Uuid;
use validator::Validate;

use crate::error::ServiceError;
use crate::models::{CreateSubmissionRequest, UpdateSubmissionRequest};
use crate::services::SubmissionService;

pub struct SubmissionHandlers {
    service: Arc<SubmissionService>,
}

impl SubmissionHandlers {
    pub fn new(service: Arc<SubmissionService>) -> Self {
        Self { service }
    }
}

#[derive(Deserialize)]
pub struct HomeworkPathParams {
    id: Uuid,
}

#[derive(Deserialize)]
pub struct SubmissionPathParams {
    id: Uuid,
}

#[derive(Deserialize)]
pub struct QueryParams {
    page: Option<i32>,
    page_size: Option<i32>,
}

#[derive(Deserialize)]
pub struct StudentQueryParams {
    student_id: Option<Uuid>,
}

impl SubmissionHandlers {
    pub async fn submit(
        &self,
        path: web::Path<HomeworkPathParams>,
        req: web::Json<CreateSubmissionRequest>,
        query: web::Query<StudentQueryParams>,
    ) -> Result<HttpResponse, ServiceError> {
        req.validate()?;
        
        let student_id = query.student_id.ok_or_else(|| {
            ServiceError::BadRequest("student_id is required".to_string())
        })?;

        let submission = self.service.submit_homework(path.id, student_id, req.into_inner()).await?;
        Ok(HttpResponse::Created().json(submission))
    }

    pub async fn get(
        &self,
        path: web::Path<SubmissionPathParams>,
    ) -> Result<HttpResponse, ServiceError> {
        let submission = self.service.get_submission(path.id).await?;
        Ok(HttpResponse::Ok().json(submission))
    }

    pub async fn list_by_homework(
        &self,
        path: web::Path<HomeworkPathParams>,
        query: web::Query<QueryParams>,
    ) -> Result<HttpResponse, ServiceError> {
        let page = query.page.unwrap_or(1);
        let page_size = query.page_size.unwrap_or(10);
        
        let result = self.service.list_submissions_by_homework(path.id, page, page_size).await?;
        Ok(HttpResponse::Ok().json(result))
    }

    pub async fn update(
        &self,
        path: web::Path<SubmissionPathParams>,
        req: web::Json<UpdateSubmissionRequest>,
        query: web::Query<StudentQueryParams>,
    ) -> Result<HttpResponse, ServiceError> {
        req.validate()?;
        
        let student_id = query.student_id.ok_or_else(|| {
            ServiceError::BadRequest("student_id is required".to_string())
        })?;

        let submission = self.service.update_submission(path.id, student_id, req.into_inner()).await?;
        Ok(HttpResponse::Ok().json(submission))
    }

    pub async fn resubmit(
        &self,
        path: web::Path<SubmissionPathParams>,
        req: web::Json<CreateSubmissionRequest>,
        query: web::Query<StudentQueryParams>,
    ) -> Result<HttpResponse, ServiceError> {
        req.validate()?;
        
        let student_id = query.student_id.ok_or_else(|| {
            ServiceError::BadRequest("student_id is required".to_string())
        })?;

        let submission = self.service.resubmit_submission(path.id, student_id, req.into_inner()).await?;
        Ok(HttpResponse::Ok().json(submission))
    }
}

pub fn configure(cfg: &mut web::ServiceConfig, handlers: Arc<SubmissionHandlers>) {
    cfg.service(
        web::scope("/api/v1/homework")
            .route("/{id}/submit", web::post().to(move |path, req, query| {
                let h = handlers.clone();
                async move { h.submit(path, req, query).await }
            }))
            .route("/{id}/submissions", web::get().to(move |path, query| {
                let h = handlers.clone();
                async move { h.list_by_homework(path, query).await }
            }))
    );

    let handlers_clone = handlers.clone();
    cfg.service(
        web::scope("/api/v1/submissions")
            .route("/{id}", web::get().to(move |path| {
                let h = handlers_clone.clone();
                async move { h.get(path).await }
            }))
            .route("/{id}", web::put().to(move |path, req, query| {
                let h = handlers_clone.clone();
                async move { h.update(path, req, query).await }
            }))
            .route("/{id}/resubmit", web::post().to(move |path, req, query| {
                let h = handlers_clone.clone();
                async move { h.resubmit(path, req, query).await }
            }))
    );
}
