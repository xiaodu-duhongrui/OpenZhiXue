use actix_web::{web, HttpResponse};
use serde::Deserialize;
use std::sync::Arc;
use uuid::Uuid;
use validator::Validate;

use crate::error::ServiceError;
use crate::models::{CreateGradeRequest, UpdateGradeRequest, BatchGradeRequest};
use crate::services::GradeService;

pub struct GradeHandlers {
    service: Arc<GradeService>,
}

impl GradeHandlers {
    pub fn new(service: Arc<GradeService>) -> Self {
        Self { service }
    }
}

#[derive(Deserialize)]
pub struct SubmissionPathParams {
    id: Uuid,
}

#[derive(Deserialize)]
pub struct GradePathParams {
    id: Uuid,
}

#[derive(Deserialize)]
pub struct HomeworkPathParams {
    id: Uuid,
}

#[derive(Deserialize)]
pub struct TeacherQueryParams {
    teacher_id: Option<Uuid>,
}

impl GradeHandlers {
    pub async fn grade(
        &self,
        path: web::Path<SubmissionPathParams>,
        req: web::Json<CreateGradeRequest>,
        query: web::Query<TeacherQueryParams>,
    ) -> Result<HttpResponse, ServiceError> {
        req.validate()?;
        
        let teacher_id = query.teacher_id.ok_or_else(|| {
            ServiceError::BadRequest("teacher_id is required".to_string())
        })?;

        let grade = self.service.grade_submission(path.id, teacher_id, req.into_inner()).await?;
        Ok(HttpResponse::Created().json(grade))
    }

    pub async fn get(
        &self,
        path: web::Path<GradePathParams>,
    ) -> Result<HttpResponse, ServiceError> {
        let grade = self.service.get_grade(path.id).await?;
        Ok(HttpResponse::Ok().json(grade))
    }

    pub async fn get_by_submission(
        &self,
        path: web::Path<SubmissionPathParams>,
    ) -> Result<HttpResponse, ServiceError> {
        let grade = self.service.get_grade_by_submission(path.id).await?;
        Ok(HttpResponse::Ok().json(grade))
    }

    pub async fn update(
        &self,
        path: web::Path<GradePathParams>,
        req: web::Json<UpdateGradeRequest>,
        query: web::Query<TeacherQueryParams>,
    ) -> Result<HttpResponse, ServiceError> {
        req.validate()?;
        
        let teacher_id = query.teacher_id.ok_or_else(|| {
            ServiceError::BadRequest("teacher_id is required".to_string())
        })?;

        let grade = self.service.update_grade(path.id, teacher_id, req.into_inner()).await?;
        Ok(HttpResponse::Ok().json(grade))
    }

    pub async fn batch_grade(
        &self,
        req: web::Json<BatchGradeRequest>,
        query: web::Query<TeacherQueryParams>,
    ) -> Result<HttpResponse, ServiceError> {
        req.validate()?;
        
        let teacher_id = query.teacher_id.ok_or_else(|| {
            ServiceError::BadRequest("teacher_id is required".to_string())
        })?;

        let grades = self.service.batch_grade(teacher_id, req.into_inner()).await?;
        Ok(HttpResponse::Created().json(grades))
    }

    pub async fn get_statistics(
        &self,
        path: web::Path<HomeworkPathParams>,
    ) -> Result<HttpResponse, ServiceError> {
        let statistics = self.service.get_homework_statistics(path.id).await?;
        Ok(HttpResponse::Ok().json(statistics))
    }

    pub async fn return_submission(
        &self,
        path: web::Path<SubmissionPathParams>,
        query: web::Query<TeacherQueryParams>,
    ) -> Result<HttpResponse, ServiceError> {
        let teacher_id = query.teacher_id.ok_or_else(|| {
            ServiceError::BadRequest("teacher_id is required".to_string())
        })?;

        self.service.return_submission(path.id, teacher_id).await?;
        Ok(HttpResponse::Ok().json(serde_json::json!({ "message": "Submission returned successfully" })))
    }
}

pub fn configure(cfg: &mut web::ServiceConfig, handlers: Arc<GradeHandlers>) {
    cfg.service(
        web::scope("/api/v1/submissions")
            .route("/{id}/grade", web::post().to(move |path, req, query| {
                let h = handlers.clone();
                async move { h.grade(path, req, query).await }
            }))
            .route("/{id}/return", web::post().to(move |path, query| {
                let h = handlers.clone();
                async move { h.return_submission(path, query).await }
            }))
    );

    let handlers_clone = handlers.clone();
    cfg.service(
        web::scope("/api/v1/grades")
            .route("/{id}", web::get().to(move |path| {
                let h = handlers_clone.clone();
                async move { h.get(path).await }
            }))
            .route("/{id}", web::put().to(move |path, req, query| {
                let h = handlers_clone.clone();
                async move { h.update(path, req, query).await }
            }))
            .route("/batch", web::post().to(move |req, query| {
                let h = handlers_clone.clone();
                async move { h.batch_grade(req, query).await }
            }))
    );

    let handlers_clone2 = handlers.clone();
    cfg.service(
        web::scope("/api/v1/homework")
            .route("/{id}/statistics", web::get().to(move |path| {
                let h = handlers_clone2.clone();
                async move { h.get_statistics(path).await }
            }))
    );
}
