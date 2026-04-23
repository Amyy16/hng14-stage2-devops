# HNG Stage 2 DevOps — Job Processing System

A containerized job processing system made up of four services:
- **Frontend** (Node.js/Express) — submits and tracks jobs
- **API** (Python/FastAPI) — creates jobs and serves status updates
- **Worker** (Python) — picks up and processes jobs from the queue
- **Redis** — shared queue between the API and worker
---

## Prerequisites

Make sure the following are installed on your machine before proceeding:

| Tool | Minimum Version | Check |
|---|---|---|
| Docker | 24.0+ | `docker --version` |
| Docker Compose | v2.0+ | `docker compose version` |
| Git | any | `git --version` |

> **Note:** Docker Compose v2 is bundled with Docker Desktop. On Linux run `sudo apt-get install docker-compose-plugin` if `docker compose` is not found.

---

## Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/Amyy16/hng14-stage2-devops.git
cd hng14-stage2-devops
```

### 2. Create your `.env` file

```bash
cp .env.example .env
```

The default values in `.env.example` work out of the box for local development. No changes needed unless you want a different frontend port.


### 3. Build and start the stack

```bash
docker compose up --build -d
```

This will:
- Build all three service images from their Dockerfiles
- Pull the Redis base image
- Start all four containers on an internal Docker network
- Run health checks on every service before marking them ready

### 4. Verify the stack is running

```bash
docker compose ps
```

Expected output — all services should show `healthy`:

```
NAME                STATUS
redis               running (healthy)
api                 running (healthy)
worker              running (healthy)
frontend            running (healthy)
```

> If a service shows `health: starting`, wait 15–30 seconds and run `docker compose ps` again. Services wait for their dependencies to be healthy before starting.

---

## Using the Application

Once the stack is up, open your browser or use curl:

### Submit a job

```bash
curl -s -X POST http://localhost:3000/submit | jq
```

Expected response:
```json
{
  "job_id": "a3f1c2d4-7e8b-4a9f-b123-456789abcdef"
}
```

### Check job status

```bash
curl -s http://localhost:3000/status/<job_id> | jq
```

Expected responses:

```json
{ "job_id": "a3f1c2d4-...", "status": "queued" }
{ "job_id": "a3f1c2d4-...", "status": "completed" }
```

> Jobs take approximately 2 seconds to process. Poll the status endpoint until you see `"completed"`.

---

## What a Successful Startup Looks Like

```
[+] Running 4/4
 ✔ Container redis     Healthy    0.5s
 ✔ Container api       Healthy   15.3s
 ✔ Container worker    Healthy   16.1s
 ✔ Container frontend  Healthy   17.4s
```

All four containers are running, all health checks pass, and the frontend is accessible at `http://localhost:3000`.

---

## Useful Commands

```bash
# View logs for all services
docker compose logs -f

# View logs for a specific service
docker compose logs -f api
docker compose logs -f worker

# Check health status of a specific container
docker inspect --format='{{.State.Health.Status}}' <container_name>

# Restart a single service
docker compose restart api

# Stop the stack
docker compose down

# Stop the stack and remove volumes
docker compose down -v

# Rebuild a single service after code changes
docker compose up -d --no-deps --build api
```

---

## Project Structure

```
hng14-stage2-devops/
├── .github/
│   └── workflows/
│       └── ci-cd.yaml       # CI/CD pipeline
├── api/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── main.py
│   ├── requirements.txt
│   ├── pytest.ini
│   └── tests/
│       ├── __init__.py
│       └── test_main.py
├── worker/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── app.js
│   ├── package.json
│   └── views/
├── docker-compose.yml
├── .env.example               # committed — placeholder values
├── .gitignore
├── README.md
└── FIXES.md
```

---

## CI/CD Pipeline

The GitHub Actions pipeline runs on every push and consists of six stages that run in strict order:

```
lint → test → build → security → integration → deploy
```

| Stage | What it does |
|---|---|
| lint | Runs flake8 (Python), eslint (JS), hadolint (Dockerfiles) |
| test | Runs pytest with Redis mocked, uploads coverage report |
| build | Builds all three images, tags with git SHA and latest, pushes to local registry |
| security | Scans all images with Trivy, fails on CRITICAL findings, uploads SARIF |
| integration | Brings full stack up, submits a job, polls until completed, tears down |
| deploy | Runs on `main` only — rolling update with 60s health check timeout |

> A failure in any stage prevents all subsequent stages from running.

---

