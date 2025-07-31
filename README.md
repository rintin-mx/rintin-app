# rintinApp

## Backend migration

A minimal FastAPI backend has been added in `backend/` to start moving logic away from Streamlit. It exposes login and register endpoints that reuse the existing database helpers.
Additional endpoints now allow listing users, retrieving permissions by email and fetching available roles.

Run it with:

```bash
uvicorn backend.main:app --reload
```

This will start an HTTP server on port 8000 by default.

### Available endpoints

* `POST /login` – authenticate a user
* `POST /register` – create a new user
* `GET /users` – list users
* `GET /users/{email}/permissions` – permissions for a user
* `GET /roles` – list roles
