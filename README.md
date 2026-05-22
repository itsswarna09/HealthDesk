# HealthDesk 🏥

> **A smart healthcare assistance platform** — built with Angular + Django + MongoDB.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Angular 17+ |
| Backend | Django 4.2 + Django REST Framework |
| Database | MongoDB (local dev) |
| Authentication | JWT (djangorestframework-simplejwt) |
| Password Hashing | bcrypt |

---

## Quick Start

### Backend

```bash
cd backend
venv\Scripts\activate          # Windows
pip install -r requirements/development.txt
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend/healthdesk-web
npm install
ng serve
```

---

## Project Structure

```
HealthDesk/
├── backend/
│   ├── apps/           # Feature apps (users, appointments, etc.)
│   ├── core/           # Shared utilities, MongoDB helper, permissions
│   ├── healthdesk/     # Django project config (settings, urls)
│   └── requirements/   # Split requirements (base/dev/prod)
├── frontend/
│   └── healthdesk-web/ # Angular app
├── docs/               # API documentation
└── CHANGELOG.md        # Project logbook
```

---

## Environment Setup

Copy `.env.example` to `.env` in the `backend/` directory and fill in your values.

---

## Current Phase: Phase 1 — Foundation

See [CHANGELOG.md](./CHANGELOG.md) for full development log.
