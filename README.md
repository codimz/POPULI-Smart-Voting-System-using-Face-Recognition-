# POPULI Smart Voting System using Face Recognition

POPULI is a campus e-voting system designed to support secure and auditable elections using face recognition and biometric verification.

## Tech Stack

* **Frontend:** Next.js 16, React 19, TypeScript
* **Database:** PostgreSQL 18
* **Containerization:** Docker & Docker Compose
* **Authentication / Verification:** Face recognition and biometric verification
* **Database Migration:** SQL migration files

## Prerequisites

Make sure the following are installed:

* Git
* Docker Desktop

Verify the installations:

```cmd
git --version
docker --version
docker compose version
```

## Getting Started

Clone the repository:

```cmd
git clone https://github.com/codimz/POPULI-Smart-Voting-System-using-Face-Recognition-.git
```

Enter the project directory:

```cmd
cd POPULI-Smart-Voting-System-using-Face-Recognition-
```

Start the development environment:

```cmd
docker compose up --build
```

After the containers are ready, open:

```text
http://localhost:3000
```

The first build may take some time because Docker needs to install dependencies and build the Next.js application.

## Services

The current Docker environment contains:

| Service    | Container         |   Port | Purpose              |
| ---------- | ----------------- | -----: | -------------------- |
| Frontend   | `populi-frontend` | `3000` | Next.js application  |
| PostgreSQL | `populi-postgres` | `5432` | Application database |

The backend API and face-recognition service are not containerized yet and will be added in later development stages.

## PostgreSQL Development Connection

The PostgreSQL container can be accessed using:

```text
Host:     localhost
Port:     5432
Database: voting_system
Username: populi
Password: populi_dev_password
```

These credentials are for the local development environment only and must not be used as production credentials.

For example, PostgreSQL can be accessed from inside the container with:

```cmd
docker exec -it populi-postgres psql -U populi -d voting_system
```

## Database Migration

The initial database schema is located at:

```text
database/migrations/001_initial_schema.sql
```

Docker Compose automatically executes this migration when the PostgreSQL database is initialized for the first time.

The migration creates the Sprint 1 tables:

* `student_dpt`
* `voting_status`
* `candidates`
* `ballot_box`
* `audit_logs`

Important: PostgreSQL initialization scripts only run when the database volume is created for the first time. If the PostgreSQL volume already exists, modifying the migration file will not automatically rerun the migration.

## Common Docker Commands

Check running containers:

```cmd
docker compose ps
```

View frontend logs:

```cmd
docker compose logs frontend
```

View PostgreSQL logs:

```cmd
docker compose logs postgres
```

Stop the environment:

```cmd
docker compose down
```

Stop the environment and remove the database volume:

```cmd
docker compose down -v
```

Then recreate the environment:

```cmd
docker compose up --build
```

> **Warning:** `docker compose down -v` permanently removes the PostgreSQL Docker volume and therefore deletes the local development database data.

## Frontend API Configuration

The frontend currently uses:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

This is currently a placeholder for the backend API.

The backend service has not yet been implemented or containerized. The API URL and Docker networking configuration will be updated when the backend is introduced.

## Project Structure

```text
POPULI-Smart-Voting-System-using-Face-Recognition-
│
├── src/
│   ├── app/
│   ├── components/
│   └── lib/
│       └── api/
│
├── database/
│   └── migrations/
│       └── 001_initial_schema.sql
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── next.config.ts
├── package.json
└── README.md
```

## Development Notes

The current Sprint 1 environment establishes the reproducible development foundation for the team:

* Next.js production build
* PostgreSQL database
* Automatic initial database migration
* Dockerized local environment
* Database constraints and relationships
* Frontend container

API contracts, backend services, and face-recognition integration will be developed in subsequent sprints.
