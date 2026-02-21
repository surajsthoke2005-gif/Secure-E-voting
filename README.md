# Secure E-Voting System with Facial Recognition and AI Authentication

Production-ready FastAPI e-voting platform with encrypted facial biometrics, blink liveness checks, OTP MFA, JWT auth, election windows, anonymous receipts, and admin auditing.

## Architecture

- `app/routers`: auth, voting, admin, and page routes
- `app/models`: SQLAlchemy models
- `app/services`: security, audit, auth helpers, OTP
- `app/ai`: OpenCV + Dlib + face_recognition module
- `app/templates` + `app/static`: responsive Tailwind/glassmorphism frontend

## Core Security Controls

- Fernet-encrypted face embeddings at rest
- bcrypt password hashing
- JWT auth for API sessions
- CSRF token issuance and verification
- Rate-limited login endpoint (`5/minute`)
- Audit logs with user, action, timestamp, and IP
- OTP (2-minute expiry, single-use)

## Required Dlib Model

Download `shape_predictor_68_face_landmarks.dat` and place it at project root (or update path in `app/ai/face_service.py`).

## Local Run (Docker)

```bash
docker compose up --build
```

App starts at `http://localhost:8000`.

## Local Run (Manual)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Render Deployment

1. Push repository to GitHub.
2. Create Render PostgreSQL service.
3. Create Render Web Service using Docker.
4. Set env vars from `.env.example` and Render DB connection string.
5. Enable HTTPS (default on Render) and deploy.

## AWS Deployment (compatible)

- Use ECS Fargate or EKS with the included Dockerfile.
- Attach RDS PostgreSQL.
- Use Secrets Manager for `SECRET_KEY`, `FERNET_KEY`, SMTP secrets.
- Put ALB with HTTPS + WAF in front of service.

## Notes

- Browser-side demo currently uses stub face embedding generation in `app/static/js/main.js`; replace with secure server-side capture pipeline for production biometric assurance.
- Votes are recorded with voter linkage for one-vote enforcement; receipt does not expose candidate selection.
