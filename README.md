# Vuettify RAG API for Cursor

FastAPI server providing Vuettify documentation assistance for Cursor AI.

## Deployment

Deployed on Render: https://your-app-name.onrender.com

## Endpoints

- `GET /` - API information
- `POST /ask` - Main coding assistant
- `GET /health` - Health check

## Local Development

```bash
pip install -r requirements.txt
uvicorn main:app --reload