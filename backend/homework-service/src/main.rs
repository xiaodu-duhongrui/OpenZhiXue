mod config;
mod db;
mod error;
mod handlers;
mod middleware;
mod models;
mod repository;
mod services;

use actix_web::{web, App, HttpServer};
use std::sync::Arc;
use log::info;

use config::Config;
use db::create_pool;
use handlers::{HomeworkHandlers, SubmissionHandlers, GradeHandlers};
use repository::{HomeworkRepository, SubmissionRepository, GradeRepository};
use services::{HomeworkService, SubmissionService, GradeService};

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv::dotenv().ok();
    env_logger::init();

    let config = Config::from_env().expect("Failed to load configuration");
    info!("Starting homework service on {}:{}", config.server.host, config.server.port);

    let pool = create_pool(&config.database)
        .await
        .expect("Failed to create database pool");

    info!("Database connection established");

    if let Err(e) = db::run_migrations(&pool).await {
        log::warn!("Migration warning: {}", e);
    }

    let homework_repo = Arc::new(HomeworkRepository::new(pool.clone()));
    let submission_repo = Arc::new(SubmissionRepository::new(pool.clone()));
    let grade_repo = Arc::new(GradeRepository::new(pool.clone()));

    let homework_service = Arc::new(HomeworkService::new(homework_repo.clone()));
    let submission_service = Arc::new(SubmissionService::new(homework_repo.clone(), submission_repo.clone()));
    let grade_service = Arc::new(GradeService::new(grade_repo.clone(), submission_repo.clone()));

    let homework_handlers = Arc::new(HomeworkHandlers::new(homework_service.clone()));
    let submission_handlers = Arc::new(SubmissionHandlers::new(submission_service.clone()));
    let grade_handlers = Arc::new(GradeHandlers::new(grade_service.clone()));

    HttpServer::new(move || {
        let mut app = App::new();

        handlers::homework::configure(&mut app, homework_handlers.clone());
        handlers::submission::configure(&mut app, submission_handlers.clone());
        handlers::grade::configure(&mut app, grade_handlers.clone());

        app.route("/health", web::get().to(health_check))
    })
    .bind((config.server.host.as_str(), config.server.port))?
    .run()
    .await
}

async fn health_check() -> actix_web::HttpResponse {
    actix_web::HttpResponse::Ok().json(serde_json::json!({
        "status": "healthy",
        "service": "homework-service"
    }))
}
