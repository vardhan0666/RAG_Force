# ⚡ RAGForge: AI Research & Knowledge Platform

An asynchronous Retrieval-Augmented Generation (RAG) platform that ingests research documents, cleans and chunks them, indexes them in a vector database, and answers questions with page-level citations.

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-DB-red?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Groq](https://img.shields.io/badge/Groq_Llama_3-F05032?style=for-the-badge)

---

## 📸 Screenshots

<!-- Add 2-3 screenshots here, for example: -->
<!-- ![Dashboard](docs/dashboard.png) -->
<!-- ![Chat with citations](docs/chat.png) -->

---

## 🌟 Key Features

- 📑 **Multi-format ingestion**: parses, cleans and indexes `.pdf`, `.docx`, `.txt`, `.md` files and web URLs.
- ⚡ **Background processing**: uploads are handled in the background, so the app doesn't block. Status goes `uploading` → `processing` → `embedding` → `indexing` → `completed`.
- 🎯 **Answers with citations**: answers from Groq Llama 3 include bracketed citations like `[1]`, `[2]` that point to the page number and text snippet they came from.
- 🔬 **Multi-document research mode**: compares several documents (similarities, differences, methods, limitations).
- 🔍 **Semantic search**: vector similarity search using Qdrant.
- 📊 **RAG Triad evaluation**: scores answers for Faithfulness, Answer Relevance and Context Precision.
- 🔐 **Authentication and data isolation**: JWT login, Bcrypt password hashing, and per-user filtering in the vector database.

---

## 🏗️ System Architecture

```text
                +---------------------------+
                |    Browser / Web Client   |
                |  (React + TS + Tailwind)  |
                +-------------+-------------+
                              |
                              | HTTP / REST
                              v
+-----------------------------------------------------------+
| Nginx Reverse Proxy                                       |
+-------------------------------+---------------------------+
                                |
                                v
+-----------------------------------------------------------+
| FastAPI Server (Uvicorn)                                  |
|  +----------------+ +-----------------+ +--------------+  |
|  | Auth (JWT)     | | Document Engine | | RAG Pipeline |  |
|  |                | | (extract/clean) | | (query, LLM) |  |
|  +----------------+ +-----------------+ +--------------+  |
+----------+------------------+------------------+----------+
           |                  |                  |
           v                  v                  v
   +---------------+  +---------------+  +----------------+
   | PostgreSQL 16 |  | Redis 7       |  | Qdrant         |
   | (users, meta) |  | (cache/state) |  | (vectors)      |
   +---------------+  +---------------+  +----------------+
```

---

## 🛠️ Tech Stack

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Axios
- **Backend:** Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Asyncpg, PyPDF, Python-Docx
- **Databases:** PostgreSQL 16 (metadata), Qdrant (vectors), Redis 7 (cache)
- **AI:** Groq API (Llama 3.1 8B Instant), through an OpenAI-compatible layer
- **DevOps:** Docker, Docker Compose, Nginx

---

## 🚀 Quick Start

You can run this project on Windows, macOS or Linux using Docker Compose.

### Prerequisites

- Git
- Docker Desktop (installed and running)

### Step 1: Clone the repository

```bash
git clone https://github.com/vardhan0666/RAG_Force.git
cd RAG_Force
```

### Step 2: Set up environment variables

Copy `.env.example` to `.env` (or create a `.env` file in the root folder) and fill it like this:

```env
# Application
PROJECT_NAME="RAGForge Platform"
API_V1_STR="/api/v1"
SECRET_KEY=change-this-to-a-long-random-string
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database
POSTGRES_SERVER=postgres
POSTGRES_USER=ragforge_user
POSTGRES_PASSWORD=change_me
POSTGRES_DB=ragforge_db
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION=ragforge_chunks

# AI (Groq)
OPENAI_API_KEY=gsk_YOUR_GROQ_API_KEY_HERE
OPENAI_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-8b-instant
EMBEDDING_MODEL=mock-embedding
EMBEDDING_DIMENSION=1536

# RAG settings
DEFAULT_CHUNK_SIZE=1000
DEFAULT_CHUNK_OVERLAP=200
DEFAULT_TOP_K=5
```

> **Notes**
> - Get a free Groq API key at [console.groq.com/keys](https://console.groq.com/keys).
> - Never upload your real `.env` file. It is listed in `.gitignore`.
> - To make a strong secret key, run: `python -c "import secrets; print(secrets.token_hex(32))"`

### Step 3: Start everything

```bash
docker compose up -d --build
```

### Step 4: Open the app

| What | URL |
|---|---|
| React web app | http://localhost |
| API docs (Swagger) | http://localhost:8000/docs |
| Qdrant dashboard | http://localhost:6333/dashboard |
| Health check | http://localhost/health |

---

## 🧪 Running Tests

```bash
docker compose exec backend pytest -v
```

---

## ⚠️ Known Limitations

- Embeddings are currently set to a **mock embedding model** (`EMBEDDING_MODEL=mock-embedding`), so retrieval is not truly semantic yet. Switching to a real embedding model is the next planned improvement.
- It is a learning project and has not been tested at large scale.

---

## 👨‍💻 Author

**Vardhan Bob**
GitHub: [@vardhan0666](https://github.com/vardhan0666)
