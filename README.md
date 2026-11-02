
# CoverCare AI

An AI-powered, restricted health insurance assistant built with FastAPI, Python, and LLM integration.

CoverCare AI helps customers understand health insurance plans, explore coverage and benefits, compare available options, and identify suitable plans based on their requirements.

The assistant is designed to operate strictly within the health insurance domain and uses company-provided insurance documentation as its knowledge source.

## Features

- **Restricted AI Assistant:** Answers health insurance-related questions only.
- **LLM Integration:** Uses an OpenAI-compatible API through FastRouter.
- **Real-Time Streaming:** Streams responses from the backend to the frontend using Server-Sent Events (SSE).
- **Insurance Knowledge Base:** Provides company-specific information from a Markdown knowledge file.
- **Plan Comparison:** Compares available insurance plans using documented information.
- **Plan Recommendations:** Helps customers explore suitable plans based on their requirements.
- **Conversation History:** Maintains context during an active chat session.
- **Input Guardrails:** Basic filtering for unrelated questions.
- **Responsive Interface:** Simple chat interface built with HTML, CSS, and JavaScript.

## Architecture

```text
                 Customer
                    |
                    v
             Frontend Client
              HTML / CSS / JS
                    |
                    | HTTP POST
                    | SSE Streaming
                    v
              FastAPI Backend
                    |
          +---------+---------+
          |                   |
          v                   v
     Guardrails          LLM Service
                              |
                              v
                       FastRouter API
                              |
                              v
                         LLM Model
                              |
                              v
                     Generated Response
                              |
                              v
                       FastAPI Backend
                              |
                              v
                      Streaming Response
                              |
                              v
                       Frontend Client
```

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| LLM Integration | OpenAI Python SDK |
| LLM Provider | FastRouter |
| Configuration | Pydantic Settings, dotenv |
| Frontend | HTML, CSS, JavaScript |
| Streaming | Server-Sent Events (SSE) |
| API Documentation | Swagger UI |
| Package Management | uv |
| Testing | Pytest, HTTPX |

## Project Structure

```text
covercare-ai/
│
├── app/
│   ├── __init__.py
│   │
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── chat.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── prompts.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── chat.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py
│   │   └── guardrail_service.py
│   │
│   └── utils/
│       └── __init__.py
│
├── data/
│   └── insurance_knowledge.md
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── tests/
│   ├── __init__.py
│   └── test_api.py
│
├── .env
├── .env.example
├── .gitignore
├── .python-version
├── pyproject.toml
├── uv.lock
└── README.md
```

## Prerequisites

Make sure you have:

- Python 3.12+
- uv package manager
- FastRouter API key
- Modern web browser

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/covercare-ai.git

cd covercare-ai
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

Create your `.env` file:

```bash
cp .env.example .env
```

Update the configuration:

```env
APP_NAME=CoverCare AI
APP_ENV=development
DEBUG=true

OPENAI_API_KEY=YOUR_FASTROUTER_API_KEY
OPENAI_MODEL=fastrouter/free
OPENAI_BASE_URL=https://api.fastrouter.ai/api/v1

MAX_HISTORY_MESSAGES=10
MAX_MESSAGE_LENGTH=2000

CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

Never commit your `.env` file or expose your API key.

### 4. Start the backend

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

Health check:

http://127.0.0.1:8000/health

### 5. Start the frontend

Open another terminal:

```bash
cd frontend

python3 -m http.server 5500
```

Open the application:

http://localhost:5500

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application information |
| GET | `/health` | Backend health check |
| POST | `/api/v1/chat/stream` | Stream AI chat responses |

### Chat API Request

```json
{
    "message": "Compare Plan A and Plan B.",
    "history": []
}
```

### Streaming Response

The backend returns Server-Sent Events:

```text
data: {"type":"token","content":"Plan A"}

data: {"type":"token","content":" provides..."}

data: {"type":"done","content":""}
```

## Insurance Knowledge Base

Insurance information is currently maintained in:

```text
data/insurance_knowledge.md
```

The knowledge base contains demonstration insurance plans:

| Plan | Annual Limit | Outpatient Limit |
|---|---:|---:|
| Plan A - Basic | $10,000 | Not included |
| Plan B - Standard | $25,000 | $1,000 |
| Plan C - Premium | $50,000 | $3,000 |

These are placeholder values for development and testing, not real insurance products.

Replace them with verified company documentation before production use.

## Testing

Run the backend tests:

```bash
uv run pytest -v
```

Check code quality:

```bash
uv run ruff check .
```

## Security and Limitations

- The assistant is restricted to health insurance-related topics.
- Responses should be grounded in the supplied company documentation.
- Missing policy information must not be invented.
- The assistant does not provide medical diagnoses or prescriptions.
- Plan recommendations are informational, not binding coverage decisions.
- Basic keyword guardrails are not a complete security solution.
- Production deployment requires stronger input validation, prompt-injection defenses, authentication, rate limiting, and monitoring.

## Development Roadmap

- [x] FastAPI backend setup
- [x] LLM API integration
- [x] Insurance knowledge base
- [x] Basic chatbot restrictions
- [x] Streaming API implementation
- [x] Frontend chat interface
- [x] Frontend-backend integration
- [ ] Improved semantic guardrails
- [ ] Intelligent insurance recommendation engine
- [ ] Structured customer requirement collection
- [ ] Persistent conversation storage
- [ ] Authentication and authorization
- [ ] Production deployment and monitoring

## Learning Objectives

This project is also a hands-on learning exercise focused on Forward Deployed Engineering (FDE), including:

- Building AI-powered applications.
- Integrating LLMs with backend services.
- Designing restricted AI assistants.
- Connecting frontend interfaces with streaming APIs.
- Working with real-world business requirements.
- Building reliable AI application architectures.

## Disclaimer

CoverCare AI is a demonstration project. The insurance plans and coverage information are sample data. Actual insurance coverage, eligibility, premiums, exclusions, and claim decisions must always be verified against official company policy documents.

## License

This project is intended for educational and development purposes.
