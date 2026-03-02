use actix_web::{web, HttpResponse};
use serde::Deserialize;
use std::sync::Arc;
use uuid::Uuid;
use validator::Validate;

use crate::error::ServiceError;
use crate::models::{
    CreateHomeworkRequest, UpdateHomeworkRequest, HomeworkListQuery, HomeworkStatus,
};
use crate::services::HomeworkService;

pub struct HomeworkHandlers {
    service: Arc<HomeworkService>,
}

impl HomeworkHandlers {
    pub fn new(service: Arc<HomeworkService>) -> Self {
        Self { service }
    }
}

#[derive(Deserialize)]
pub struct PathParams {
    id: Uuid,
}

#[derive(Deserialize)]
pub struct ClassPathParams {
    class_id: Uuid,
}

#[derive(Deserialize)]
pub struct QueryParams {
    class_id: Option<Uuid>,
    teacher_id: Option<Uuid>,
    subject: Option<String>,
    status: Option<String>,
    page: Option<i32>,
    page_size: Option<i32>,
}

impl HomeworkHandlers {
    pub async fn create(
        &self,
        req: web::Json<CreateHomeworkRequest>,
    ) -> Result<HttpResponse, ServiceError> {
        req.validate()?;
        
        let homework = self.service.create_homework(req.into_inner()).await?;
        Ok(HttpResponse::Created().json(homework))
    }

    pub async fn get(
        &self,
        path: web::Path<PathParams>,
    ) -> Result<HttpResponse, ServiceError> {
        let homework = self.service.get_homework(path.id).await?;
        Ok(HttpResponse::Ok().json(homework))
    }

    pub async fn list(
        &self,
        query: web::Query<QueryParams>,
    ) -> Result<HttpResponse, ServiceError> {
        let status = query.status.as_ref().and_then(|s| match s.to_lowercase().as_str() {
            "draft" => Some(HomeworkStatus::Draft),
            "published" => Some(HomeworkStatus::Published),
            "closed" => Some(HomeworkStatus::Closed),
            "archived" => Some(HomeworkStatus::Archived),
            _ => None,
        });

        let query = HomeworkListQuery {
            class_id: query.class_id,
            teacher_id: query.teacher_id,
            subject: query.subject.clone(),
            status,
            page: query.page,
            page_size: query.page_size,
        };

        let result = self.service.list_homework(query).await?;
        Ok(HttpResponse::Ok().json(result))
    }

    pub async fn list_by_class(
        &self,
        path: web::Path<ClassPathParams>,
        query: web::Query<QueryParams>,
    ) -> Result<HttpResponse, ServiceError> {
        let page = query.page.unwrap_or(1);
        let page_size = query.page_size.unwrap_or(10);
        
        let result = self.service.list_homework_by_class(path.class_id, page, page_size).await?;
        Ok(HttpResponse::Ok().json(result))
    }

    pub async fn update(
        &self,
        path: web::Path<PathParams>,
        req: web::Json<UpdateHomeworkRequest>,
    ) -> Result<HttpResponse, ServiceError> {
        req.validate()?;
        
        let homework = self.service.update_homework(path.id, req.into_inner()).await?;
        Ok(HttpResponse::Ok().json(homework))
    }

    pub async fn delete(
        &self,
        path: web::Path<PathParams>,
    ) -> Result<HttpResponse, ServiceError> {
        self.service.delete_homework(path.id).await?;
        Ok(HttpResponse::NoContent().finish())
    }

    pub async fn publish(
        &self,
        path: web::Path<PathParams>,
    ) -> Result<HttpResponse, ServiceError> {
        let homework = self.service.publish_homework(path.id).await?;
        Ok(HttpResponse::Ok().json(homework))
    }

    pub async fn close(
        &self,
        path: web::Path<PathParams>,
    ) -> Result<HttpResponse, ServiceError> {
        let homework = self.service.close_homework(path.id).await?;
        Ok(HttpResponse::Ok().json(homework))
    }

    pub async fn archive(
        &self,
        path: web::Path<PathParams>,
    ) -> Result<HttpResponse, ServiceError> {
        let homework = self.service.archive_homework(path.id).await?;
        Ok(HttpResponse::Ok().json(homework))
    }
}

pub fn configure(cfg: &mut web::ServiceConfig, handlers: Arc<HomeworkHandlers>) {
    cfg.service(
        web::scope("/api/v1/homework")
            .route("", web::post().to(move |req| {
                let h = handlers.clone();
                async move { h.create(req).await }
            }))
            .route("", web::get().to(move |query| {
                let h = handlers.clone();
                async move { h.list(query).await }
            }))
            .route("/{id}", web::get().to(move |path| {
                let h = handlers.clone();
                async move { h.get(path).await }
            }))
            .route("/{id}", web::put().to(move |path, req| {
                let h = handlers.clone();
                async move { h.update(path, req).await }
            }))
            .route("/{id}", web::delete().to(move |path| {
                let h = handlers.clone();
                async move { h.delete(path).await }
            }))
            .route("/{id}/publish", web::post().to(move |path| {
                let h = handlers.clone();
                async move { h.publish(path).await }
            }))
            .route("/{id}/close", web::post().to(move |path| {
                let h = handlers.clone();
                async move { h.close(path).await }
            }))
            .route("/{id}/archive", web::post().to(move |path| {
                let h = handlers.clone();
                async move { h.archive(path).await }
            }))
    );

    let handlers_clone = handlers.clone();
    cfg.service(
        web::scope("/api/v1/classes")
            .route("/{class_id}/homework", web::get().to(move |path, query| {
                let h = handlers_clone.clone();
                async move { h.list_by_class(path, query).await }
            }))
    );
}
