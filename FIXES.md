# 🛠️ FIXES.md

## Overview

This document outlines all identified issues in the provided codebase, including bugs, misconfigurations, and bad practices. Each issue is documented with the affected file, the problem, and the fix applied.

---

## 🔧 API Service Fixes (`api/`)

### 1. Environment file committed (Bad Practice)

* **File:** `api/.env`

* **Problem:**
  The `.env` file was present in the repository, which is a security risk and violates best practices. Sensitive configuration should never be committed to version control.

* **Fix:**

  * Added `.env` to `.gitignore`
    ̵ Created `.env.example` with placeholder values for required environment variables

---

### 2. Hardcoded Redis Configuration

* **File:** `api/main.py` (Line 8)

* **Problem:**
  Redis host and port were hardcoded (`localhost:6379`), which breaks in containerized environments where services communicate via service names.

* **Fix:**
  Replaced hardcoded values with environment variables:

```python
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
```

---

### 3. No Redis Connection Error Handling

* **File:** `api/main.py` (Line 8)

* **Problem:**
  Redis connection was initialized without handling connection failures, which could cause runtime crashes.

* **Fix:**
  Wrapped Redis connection logic in a try-except block to handle connection failures gracefully.

---

## 🔧 Frontend Service Fixes (`frontend/`)

### 4. Hardcoded API URL

* **File:** `frontend/index.js` (Line 6)

* **Problem:**
  API URL was hardcoded to `http://localhost:8000`, which fails in Docker since `localhost` refers to the container itself.

* **Fix:**
  Replaced with environment variable:

```javascript
const API_URL = process.env.API_URL || "http://localhost:8000";
```

---

## 🔧 Worker Service Fixes (`worker/`)

### 5. Hardcoded Redis Configuration

* **File:** `worker/main.py` (Line 6)

* **Problem:**
  Redis host was hardcoded, making the service incompatible with Docker networking.

* **Fix:**
  Replaced with environment variables:

```python
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
```

---

### 6. No Redis Connection Error Handling

* **File:** `worker/main.py` (Line 6)

* **Problem:**
  Redis connection was not protected against failures, which could crash the worker.

* **Fix:**
  Wrapped Redis connection in a try-except block to ensure proper error handling.

---

### 7. No Graceful Shutdown Handling

* **File:** `worker/worker.py`

* **Problem:**
  The worker did not handle termination signals. When Docker stops a container, it sends a `SIGTERM`. Without handling this, the worker could be terminated mid-job, leading to inconsistent state.

* **Fix:**
  Added signal handlers for `SIGTERM` and `SIGINT`:

  * Introduced a shutdown flag
  * Allowed the worker to complete the current job before exiting cleanly

---

