# AI Test Case Generator

This repository contains a full-stack AI-powered test case generation agent.
It includes:

- `frontend/` — Next.js app for input, generation, and dashboard display.
- `backend/` — FastAPI service for requirement parsing, constraint extraction, rule-based test generation, edge-case expansion, and optional AI enrichment.

## Project location
All project files are located under:

`C:\Users\Asus\ai-test-generator`

## Running locally

### Backend only

1. Open a terminal in `C:\Users\Asus\ai-test-generator\backend`
2. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Run the backend:
   ```powershell
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend only

1. Open a terminal in `C:\Users\Asus\ai-test-generator\frontend`
2. Install dependencies:
   ```powershell
   npm install
   ```
3. Run the frontend:
   ```powershell
   npm run dev
   ```

### Full stack via Docker Compose

From `C:\Users\Asus\ai-test-generator` run:
```powershell
docker compose up --build
```

## Backend endpoint
- `POST http://localhost:8000/generate`

Request body example:
```json
{
  "requirements": "Password must be >= 8 characters, age 18-60, email format"
}
```

## Notes
- The backend supports optional OpenAI enrichment if `OPENAI_API_KEY` is set in `.env`.
- The frontend is configured to call the backend on `http://localhost:8000/generate`.
