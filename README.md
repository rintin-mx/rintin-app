# rintinApp

## Backend migration

A minimal FastAPI backend has been added in `backend/` to start moving logic away from Streamlit. It exposes login and register endpoints that reuse the existing database helpers.

Run it with:

```bash
uvicorn backend.main:app --reload
```

This will start an HTTP server on port 8000 by default.
