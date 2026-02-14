# Plex ToDo AI Backend

Current Version: 1.2.0 (Render Deployment)
- **Live Demo:** [https://plex-todo-ai.onrender.com/docs](https://plex-todo-ai.onrender.com/docs)
- **GitHub Repository:** [https://github.com/Ubbix1/plex_todo_ai](https://github.com/Ubbix1/plex_todo_ai)
- **Download Android App:** [plex_todo.apk](Apk/plex_todo.apk)

A robust, offline-capable AI backend for the **Plex ToDo** application. This service parses natural language into structured To-Do tasks using the **Hugging Face Inference API**, making it lightweight and deployable on free-tier platforms like Render and PythonAnywhere.

## Features

-   **Hosted AI Inference**: Uses Hugging Face API (TinyLlama-1.1B) instead of heavy local models.
-   **Lightweight**: Minimal dependencies (no `torch`, `transformers`), installs in seconds.
-   **FastAPI Powered**: High-performance, async-ready Python framework.
-   **Type-Safe**: Full Pydantic validation for inputs and outputs.
-   **Deployment Ready**: includes WSGI adapter for PythonAnywhere (see [Deployment Guide](DEPLOY.md)).

## Prerequisites

-   Python 3.10+
-   **Hugging Face API Token** (Free)

## Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up environment variables:
    -   Copy `.env.example` to `.env`
    -   Add your Hugging Face API key: `HF_API_KEY=hf_...`

## Usage

### Running Locally

```bash
uvicorn main:app --reload
```
The server will start at `http://127.0.0.1:8000`.

### API Endpoint

**POST** `/parse-task`

#### Live Example
```bash
curl -X POST "https://plex-todo-ai.onrender.com/parse-task" \
     -H "Content-Type: application/json" \
     -d '{"text": "Call John every Friday at 10am"}'
```

#### Request Format
```json
{
  "text": "Call John every Friday at 10am"
}
```

#### Response Format
```json
{
  "title": "Call John",
  "time": "10:00",
  "date": null,
  "repeat": "weekly on friday",
  "priority": "medium"
}
```

## Documentation

-   [**Deployment Guide**](DEPLOY.md): Step-by-step guide to deploy.
-   [**Swagger UI (Live)**](https://plex-todo-ai.onrender.com/docs): Interactive API documentation.
-   [**Swagger UI (Local)**](http://127.0.0.1:8000/docs): Local API documentation.

## Testing

Run the test suite (mocks the API calls):

```bash
pytest
```
