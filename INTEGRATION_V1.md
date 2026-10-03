# PillSync Integration V1

This branch was upgraded from a UI/prototype state to a backend-connected MVP.

## Implemented in this version

- JWT access/refresh authentication with role claims.
- Patient/caregiver registration; patient registration automatically creates a primary profile.
- Protected REST APIs by default.
- Profile ownership checks.
- Medication CRUD connected to the React frontend.
- Medication schedule creation and retrieval connected to the frontend.
- Adherence logs stored in Django instead of browser seed/local-storage data.
- Backend-derived adherence analytics and seven-day trends.
- Refill prediction connected to actual medicine stock.
- Refill prediction records persisted when a medicine is supplied.
- Tesseract OCR image endpoint plus a text parser with confidence estimation.
- Celery/Redis configuration and an idempotent daily reminder-generation task.
- PostgreSQL configuration through environment variables while retaining SQLite for local fallback.
- Docker backend entrypoint runs migrations before starting Django.

## Important limitations

This is an integration MVP, not a production healthcare deployment.

Still to be completed:

- OAuth2/Google login provider integration.
- Real caregiver-to-patient assignment model and caregiver-specific authorization.
- Email/SMS/push delivery provider integration (SendGrid/Twilio/FCM).
- Full admin user-management API and audit logging.
- Clinical-grade OCR validation and human confirmation workflow.
- Production secrets, HTTPS, secure CORS policy, rate limiting and monitoring.
- Full end-to-end and browser test suite.

## Local backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements/base.txt
python manage.py migrate
python manage.py runserver
```

## Local frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects `VITE_API_BASE_URL=http://localhost:8000/api` by default.

## Docker

```bash
cp backend/.env.example backend/.env
# On Windows PowerShell use: Copy-Item backend/.env.example backend/.env
docker compose up --build
```

The backend uses PostgreSQL when `POSTGRES_DB` is set and SQLite otherwise.
