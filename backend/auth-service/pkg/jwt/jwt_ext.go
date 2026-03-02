package jwt

import "time"

func (s *JWTService) AccessTokenExpire() int {
	return s.accessTokenExpire
}

func (s *JWTService) RefreshTokenExpire() int {
	return s.refreshTokenExpire
}

func (s *JWTService) Secret() string {
	return s.secret
}

func (s *JWTService) Issuer() string {
	return s.issuer
}
