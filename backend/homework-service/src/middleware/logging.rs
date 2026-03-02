use actix_web::{dev::Service, dev::Transform, dev::ServiceRequest, dev::ServiceResponse, Error};
use futures::future::{ready, Ready, LocalBoxFuture};
use std::rc::Rc;
use std::task::{Context, Poll};
use std::time::Instant;
use log::info;

pub struct LoggingMiddleware;

impl<S, B> Transform<S, ServiceRequest> for LoggingMiddleware
where
    S: Service<ServiceRequest, Response = ServiceResponse<B>, Error = Error> + 'static,
    S::Future: 'static,
    B: 'static,
{
    type Response = ServiceResponse<B>;
    type Error = Error;
    type InitError = ();
    type Transform = LoggingMiddlewareService<S>;
    type Future = Ready<Result<Self::Transform, Self::InitError>>;

    fn new_transform(&self, service: S) -> Self::Future {
        ready(Ok(LoggingMiddlewareService {
            service: Rc::new(service),
        }))
    }
}

pub struct LoggingMiddlewareService<S> {
    service: Rc<S>,
}

impl<S, B> Service<ServiceRequest> for LoggingMiddlewareService<S>
where
    S: Service<ServiceRequest, Response = ServiceResponse<B>, Error = Error> + 'static,
    S::Future: 'static,
    B: 'static,
{
    type Response = ServiceResponse<B>;
    type Error = Error;
    type Future = LocalBoxFuture<'static, Result<Self::Response, Self::Error>>;

    fn poll_ready(&self, ctx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
        self.service.poll_ready(ctx)
    }

    fn call(&self, req: ServiceRequest) -> Self::Future {
        let service = self.service.clone();
        let start = Instant::now();
        let method = req.method().to_string();
        let path = req.path().to_string();

        Box::pin(async move {
            let res = service.call(req).await?;
            let duration = start.elapsed();
            info!(
                "{} {} - {}ms - {}",
                method,
                path,
                duration.as_millis(),
                res.status()
            );
            Ok(res)
        })
    }
}
