use actix_web::{dev::ServiceRequest, Error, HttpMessage};
use actix_web_httpauth::extractors::bearer::BearerAuth;
use jsonwebtoken::{decode, Algorithm, DecodingKey, Validation};
use serde::{Deserialize, Serialize};

use crate::config::JwtConfig;
use crate::error::ServiceError;

#[derive(Debug, Serialize, Deserialize)]
pub struct Claims {
    pub sub: String,
    pub role: String,
    pub exp: usize,
    pub iat: usize,
}

#[derive(Clone)]
pub struct AuthMiddleware {
    jwt_config: JwtConfig,
}

impl AuthMiddleware {
    pub fn new(jwt_config: JwtConfig) -> Self {
        Self { jwt_config }
    }

    pub fn validate_token(&self, token: &str) -> Result<Claims, ServiceError> {
        decode::<Claims>(
            token,
            &DecodingKey::from_secret(self.jwt_config.secret.as_bytes()),
            &Validation::new(Algorithm::HS256),
        )
        .map(|data| data.claims)
        .map_err(|_| ServiceError::Unauthorized("Invalid token".to_string()))
    }

    pub fn extract_user_id(&self, req: &ServiceRequest) -> Result<String, ServiceError> {
        req.extensions()
            .get::<Claims>()
            .map(|claims| claims.sub.clone())
            .ok_or_else(|| ServiceError::Unauthorized("User not authenticated".to_string()))
    }
}

pub async fn validator(
    req: ServiceRequest,
    credentials: BearerAuth,
) -> Result<ServiceRequest, (Error, ServiceRequest)> {
    let config = req
        .app_data::<actix_web::web::Data<AuthMiddleware>>()
        .map(|d| d.get_ref().clone());

    if let Some(auth_middleware) = config {
        match auth_middleware.validate_token(credentials.token()) {
            Ok(claims) => {
                req.extensions_mut().insert(claims);
                Ok(req)
            }
            Err(e) => Err((e.into(), req)),
        }
    } else {
        Err((ServiceError::InternalError("Auth middleware not configured".to_string()).into(), req))
    }
}
