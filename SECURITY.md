# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in OpenZhixue, please report it responsibly.

### How to Report

**Do NOT create a public GitHub issue for security vulnerabilities.**

Instead, please report security issues by:

1. **Email**: Send details to security@openzhixue.example.com
2. **GitHub Security Advisory**: Use [GitHub's private vulnerability reporting](https://github.com/your-org/openzhixue/security/advisories/new)

### What to Include

Please include the following information in your report:

- Type of vulnerability (e.g., XSS, SQL injection, authentication bypass)
- Full path or URL where the vulnerability was discovered
- Steps to reproduce the issue
- Proof-of-concept or exploit code (if available)
- Potential impact of the vulnerability
- Your contact information for follow-up

### Response Timeline

| Stage | Expected Time |
|-------|---------------|
| Initial Response | Within 48 hours |
| Triage & Assessment | Within 5 business days |
| Fix Development | Depends on severity |
| Security Advisory | After fix is released |

### Disclosure Policy

- We follow **responsible disclosure** practices
- Please do not disclose the vulnerability publicly until a fix has been released
- We will credit you in our security advisory (unless you prefer to remain anonymous)

## Security Best Practices

When deploying OpenZhixue, please follow these security recommendations:

### Authentication & Authorization

- Change all default passwords immediately after deployment
- Use strong, unique passwords for all service accounts
- Enable multi-factor authentication (MFA) where available
- Regularly rotate API keys and access tokens

### Network Security

- Deploy services behind a firewall
- Use TLS/SSL for all external communications
- Restrict database access to internal network only
- Enable rate limiting on API Gateway

### Data Protection

- Encrypt sensitive data at rest (database encryption)
- Use environment variables for secrets, never commit them to version control
- Regularly backup databases and test restore procedures
- Implement data retention policies according to local regulations

### Infrastructure

- Keep all dependencies up to date
- Regularly apply security patches to underlying systems
- Monitor logs for suspicious activities
- Use container security scanning for Docker images

### Secrets Management

```bash
# Never commit .env files
# Use .env.example as a template
cp .env.example .env
# Edit with your actual secrets
```

## Security Features

OpenZhixue includes the following security features:

| Feature | Description |
|---------|-------------|
| JWT Authentication | Secure token-based authentication |
| RBAC | Role-based access control |
| Rate Limiting | API rate limiting at gateway level |
| Input Validation | Comprehensive input sanitization |
| Audit Logging | Operation logging for accountability |
| Password Hashing | Secure password storage with bcrypt |

## Security Updates

Security updates will be announced through:

- GitHub Security Advisories
- Release notes with `security` label
- Email notifications to registered users

## Acknowledgments

We would like to thank all security researchers who responsibly disclose vulnerabilities to help keep OpenZhixue secure.

---

For general security questions (non-vulnerability reports), please open a GitHub Discussion.
