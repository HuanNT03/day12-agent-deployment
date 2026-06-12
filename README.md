# Clothes Recommendation ReAct Agent (Day 12 Cloud Deployment Lab)

This repository contains a production-ready Clothes Recommendation ReAct Agent built using FastAPI, Pydantic, and Uvicorn. The repository is optimized for deployment using Docker, Docker Compose, and cloud platforms like Railway or Render.

## 📁 Repository Structure

```text
your-repo/
├── app/
│   ├── main.py              # Main application (Entrypoint & ReAct Loop)
│   ├── config.py            # Configuration (12-Factor Env Loader)
│   ├── auth.py              # Authentication (API Key Protection)
│   ├── rate_limiter.py      # Rate limiting (Redis / In-memory sliding window)
│   └── cost_guard.py        # Cost protection (Daily USD budget guard)
├── utils/
│   └── mock_llm.py          # Mock LLM provider (Fallback)
├── screenshots/             # Screenshots of the deployment and API calls
├── Dockerfile               # Multi-stage production Docker build
├── docker-compose.yml       # Full stack local composer (FastAPI + Redis)
├── requirements.txt         # Project dependencies
├── .env.example             # Template environment variables
├── .dockerignore            # Docker ignore file
├── railway.toml             # Railway configuration
└── README.md                # This setup instructions file
```

---

## 🚀 Getting Started

### 1. Prerequisite Configuration

Clone the repository and copy the environment template file:
```bash
cp .env.example .env
```
Fill out the variables inside `.env`. If you do not have a `DASHSCOPE_API_KEY`, the agent will run in simulation (mock ReAct loop) mode using mock weather and recommendations.

### 2. Local Run (FastAPI Development)

First, install dependencies:
```bash
pip install -r requirements.txt
```

Run the FastAPI application with reload enabled:
```bash
python app/main.py
```
Or run using Uvicorn directly:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🐳 Docker Stack

### Local Development with Docker Compose

To run the full stack (FastAPI + Redis) locally, run:
```bash
docker compose up --build
```
This maps the agent to port `80` on your host.

### Production Docker Run

To build the production container image manually:
```bash
docker build -t ai-agent:latest .
```

To run the container stand-alone:
```bash
docker run -p 8000:8000 --env-file .env ai-agent:latest
```

---

## 🌐 API Reference

Always pass `X-API-Key` in the request headers (configured via `AGENT_API_KEY` in `.env`).

### `POST /ask`
Submit a clothing query or weather consultation.

- **Headers:**
  - `X-API-Key: <your-key>`
  - `Content-Type: application/json`
- **Body:**
  ```json
  {
    "question": "Tôi định đi chơi ở Hà Nội vào ngày 2026-06-01. Hãy gợi ý trang phục giúp tôi dựa trên thời tiết nhé."
  }
  ```
- **Response:**
  ```json
  {
    "question": "Tôi định đi chơi ở Hà Nội vào ngày 2026-06-01. Hãy gợi ý trang phục giúp tôi dựa trên thời tiết nhé.",
    "answer": "Dự báo thời tiết tại Hà Nội ngày 2026-06-01: nhiệt độ khoảng 27°C - 32°C, khả năng mưa 70%. Gợi ý trang phục phù hợp cho bạn: Áo mưa, giày dễ khô, mang theo ô gấp. (Đây là mock response từ ReAct Loop).",
    "model": "qwen-turbo",
    "timestamp": "2026-06-12T14:00:00.000Z"
  }
  ```

### `GET /health`
Liveness probe.

### `GET /ready`
Readiness probe. Checks dependency health (like Redis connection).

### `GET /metrics`
Protected metrics API (requires API key header).
```json
{
  "uptime_seconds": 150.5,
  "total_requests": 2,
  "error_count": 0,
  "daily_cost_usd": 0.0002,
  "daily_budget_usd": 5.0,
  "budget_used_pct": 0.0
}
```

---

## 🔍 Validation Checklist

To check if the project is ready for deployment:
```bash
python check_production_ready.py
```
This ensures multi-stage builds, non-root user permissions, health check endpoints, API keys, rate limit protection, and proper `.gitignore` setups are fully compliant.
