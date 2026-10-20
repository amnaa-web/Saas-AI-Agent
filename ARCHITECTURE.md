# Suggested Production Architecture

## Frontend
Next.js / React
- Candidate portal
- Employer portal
- Company admin
- Verification officer dashboard
- Platform admin
- Responsive mobile-first candidate flows

## Backend
NestJS / Node.js
- Tenant-aware API layer
- RBAC
- Verification workflow state machine
- Matching service
- Subscription service
- E-signature service
- Audit service
- Notification service

## Storage
PostgreSQL
- tenants
- users
- roles
- candidate profiles
- qualifications
- verification records
- subscriptions
- recruitment pipelines
- match decisions
- contracts
- audit logs

AWS S3 EU region
- certificates
- signed contracts
- supporting documents

## Matching
1. Natural-language requirement extraction
2. Employer review / approval of criteria
3. Mandatory deterministic filters
4. Weighted ranking
5. AI-assisted explanation
6. Verification-state display
7. Rule-based fallback when AI is unavailable

## Security / GDPR
- EU / EEA processing
- tenant isolation
- RBAC
- admin MFA
- encryption in transit and at rest
- consent / legal-basis records
- data export / correction / deletion workflows
- retention policies
- audit logs
- rate limiting / anti-scraping
- backups + tested recovery

## Integrations
- Stripe
- Oneflow or Scrive
- email / SMS provider
- future BankID
- future ID06
- accounting / certification providers