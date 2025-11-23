# Booking Agenda – Meeting Room Reservation System

Booking Agenda is a small **meeting room reservation system** built with:

- **FastAPI** + **SQLAlchemy** (backend, REST API)
- **PostgreSQL** (database)
- **Static HTML + JavaScript + Nginx** (frontend)
- **Docker Compose** (orchestration of 4 containers)

It is designed as a **university / enterprise-style** booking tool where users can:

- Create, edit and delete their own reservations
- Avoid overlapping time slots (global calendar conflict check)
- See a **weekly preview** of the current week with all reserved slots
- Register new accounts from a dedicated registration page

Admins can view and manage all reservations in the system.

---

## Features

### User & Authentication

- User registration (email, full name, password)
- Login with email + password
- Passwords hashed using `passlib` (`pbkdf2_sha256`)
- JWT-based authentication with FastAPI’s `OAuth2PasswordBearer`
- `/me` endpoint to get the current user profile
- Admin flag (`is_admin`) on users

### Reservations

- Create, update, delete reservations
- Each reservation has:
  - Title
  - Description
  - Start date & time
  - End date & time
  - Owner (linked to User)
- **Global conflict detection**:
  - No two reservations can overlap in time, regardless of user
  - If a conflict exists, backend returns HTTP 400 with an explanatory message

### Frontend

- Login page (`index.html`):
  - Simple, clean UI
  - Email + password login
  - Button to go to registration page
  - Create / update reservation form
  - Buttons to view “My reservations” or “All reservations”
  - Weekly preview of the current week (Mon–Sun) showing:
    - Time range
    - Meeting title
    - Owner name

- Registration page (`register.html`):
  - Separate page only for user registration
  - Fields: email, full name, password, confirm password
  - Returns to login after successful registration

---

## Architecture

The project is organized in **4 main containers** (via `docker-compose`):

1. **db**  
   - PostgreSQL 15  
   - Stores users and reservations

2. **backend**  
   - Python 3.11  
   - FastAPI application  
   - SQLAlchemy ORM models  
   - JWT authentication  
   - Exposed on port `8000`

3. **frontend**  
   - Nginx (serving static HTML/JS)  
   - Exposed on port `3000`  
   - Talks to the backend at `http://localhost:8000`

4. **pgadmin** (optional but included)  
   - pgAdmin4 web UI  
   - For inspecting and managing the PostgreSQL database

---

## Tech Stack

- **Backend**
  - Python 3.11
  - FastAPI
  - SQLAlchemy
  - Pydantic v2
  - PostgreSQL (via `psycopg2-binary`)
  - passlib (`pbkdf2_sha256`)
  - python-multipart (for auth form)
  - python-jose (JWT)

- **Frontend**
  - Static HTML + CSS + JavaScript
  - Served by Nginx (alpine image)

- **Infrastructure**
  - Docker
  - Docker Compose
  - pgAdmin4 (database GUI)

---

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) installed  
- [Docker Compose](https://docs.docker.com/compose/) installed  
- A GitHub SSH key set up if you’re cloning via SSH (optional but recommended)

### Clone the repository

```bash
git clone git@github.com:Utp-AE/Booking-Agenda.git
cd Booking-Agenda
The backend supports a few environment variables (with sensible defaults):

DATABASE_URL
Default (inside Docker):
postgresql+psycopg2://meeting_user:meeting_pass@db:5432/meeting_db

SECRET_KEY
Default: "Pochita_2025" (override this in production)

ALGORITHM
Default: "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES
Default: 60

You can set these in docker-compose.yml under the backend service if needed.

Run the stack

From the project root:
docker-compose up --build
This will:

Build the backend and frontend images

Download PostgreSQL and pgAdmin images (if not present)

Start all containers

Accessing the application

Once docker-compose is running:

Frontend (UI):
👉 http://localhost:3000

Backend API docs (Swagger):
👉 http://localhost:8000/docs

pgAdmin (optional):
👉 http://localhost:5050
Credentials are defined in docker-compose.yml (e.g. admin@example.com / admin).
Usage
1. Register a new user

Go to the frontend: http://localhost:3000

Click “Registrarse” (Register):

This opens register.html in a new page.

Fill in:

Correo institucional (email)

Nombre completo (full name)

Contraseña (password)

Confirmar contraseña (password confirmation)

Submit. On success, you’ll be redirected back to the login page.

By default, users registered from the web are not admins (is_admin = false).

If you need an admin account, you can:

Use /register endpoint directly from Swagger and set is_admin = true, or

Update a user row in the database (is_admin = true) via pgAdmin.

2. Login

On index.html, enter:

Email

Password

Click “Iniciar sesión”.

If successful:

A JWT token is obtained via /token.

The frontend stores it in memory and uses it in Authorization: Bearer <token> headers.

The top-right badge shows your name/email and role (Usuario/Administrador).

3. Create a reservation

After login, in the Nueva reserva (New reservation) section:

Título

Descripción (optional)

Inicio (datetime-local)

Fin (datetime-local)

Click “Crear reserva”.

The backend will:

Check for any existing reservation whose time overlaps with the range.

If there is a conflict, it returns HTTP 400 with a message:

"Ya existe una reserva en ese rango de tiempo. Por favor seleccione otro horario."

On success, the reservation is created and the UI updates:

“Mis reservas” list

Weekly preview

4. View reservations

In the Ver reservas section:

Click “Mis reservas”:

Shows only reservations owned by the current user.

Click “Todas las reservas”:

If you are admin, shows all reservations.

If you are a normal user, it behaves like “Mis reservas”.

Each reservation card shows:

Title and ID

Owner (name or email)

Start and end times

Description

A button to delete the reservation

5. Update a reservation

Take note of the reservation ID you want to edit.

Put that ID in the “ID de reserva (solo para editar)” field.

Adjust title, description, start and end dates/times.

Click “Actualizar reserva”.

The backend ensures:

Only the owner or an admin can modify a reservation.

The new time range does not overlap with other reservations.

6. Delete a reservation

Click “Eliminar” on the reservation card.

The backend ensures:

Only the owner or an admin can delete a reservation.

Weekly Preview (Current Week)

At the bottom of the main page there is a “Resumen semanal de reservas” card. It shows:

The current week (Monday–Sunday)

For each day:

If there are reservations:

Time range (HH:MM–HH:MM)

Title of the meeting

Owner name/email

If there are no reservations:

“Sin reservas”

This helps users visually avoid choosing already reserved slots.

API Reference (high-level)

All endpoints are under the backend base URL: http://localhost:8000.

POST /register
Create a new user.
Body: UserCreate (email, full_name, password, is_admin).

POST /token
Login with form data (username, password).
Returns a JWT: { access_token, token_type }.

GET /me
Get current user info (requires Authorization: Bearer <token>).

GET /reservations?mine=true|false
List reservations:

mine=true: only current user reservations.

mine=false: all reservations (admin) or user’s own if not admin.

POST /reservations
Create reservation (requires auth).
Body: ReservationCreate.

PUT /reservations/{id}
Update reservation (owner or admin only, no conflicts allowed).

DELETE /reservations/{id}
Delete reservation (owner or admin only).

Swagger auto-docs available at: http://localhost:8000/docs.

Project Structure
Booking-Agenda/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI entry point
│   │   ├── models.py        # SQLAlchemy models (User, Reservation)
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── auth.py          # Auth & JWT utilities
│   │   └── database.py      # DB engine, Session, Base
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── index.html           # Main UI (login + reservations + weekly preview)
│   ├── register.html        # Separate registration page
│   └── Dockerfile
│
├── docker-compose.yml       # Orchestrates db, backend, frontend, pgadmin
└── README.md

Development Notes & Future Improvements

Possible future enhancements:

Support for multiple rooms (e.g., Room A, Room B, etc.).

Timezone support / configuration.


You can save that as `README.md` in your repo root and commit/push it.


User roles with more granularity (e.g., department-level admins).

Email notifications on reservation creation/update/cancellation.

UI improvements with a full calendar library (e.g., FullCalendar).
