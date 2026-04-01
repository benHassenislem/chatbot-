# AI Chatbot

A simple AI chatbot built with **Flask** and the **OpenAI API**, featuring a clean web interface and conversation history.

## Project Structure

```
test chatbot/
├── app.py                 # Flask backend — API endpoints & AI logic
├── static/
│   └── index.html         # Chat UI (HTML + CSS + JavaScript)
├── .env                   # Environment variables (your secrets — not committed)
├── .env.example           # Template for .env
├── requirements.txt       # Python dependencies
├── .gitignore
└── README.md
```

## Quick Start

### 1. Create & activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your OpenAI API key

Edit `.env` and replace `sk-YOUR-KEY-HERE` with your actual key from
[platform.openai.com/api-keys](https://platform.openai.com/api-keys):

```
OPENAI_API_KEY=sk-proj-abc123...
```

### 4. Run the server

```bash
python app.py
```

### 5. Open the chatbot

Visit **http://localhost:5000** in your browser.

## API Reference

| Method | Endpoint           | Body                        | Description                |
| ------ | ------------------ | --------------------------- | -------------------------- |
| POST   | `/api/chat`        | `{ "message": "Hi!" }`     | Send a message, get reply  |
| POST   | `/api/chat/reset`  | —                           | Clear conversation history |
| GET    | `/`                | —                           | Serve the chat UI          |

### Example curl request

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Python?"}'
```

## Architecture Overview

```
Browser (index.html)
    │
    │  POST /api/chat  { "message": "..." }
    ▼
Flask Backend (app.py)
    │
    │  Maintains per-session conversation history
    │  Builds messages array: [system_prompt, ...history]
    ▼
OpenAI Chat Completions API
    │
    │  Returns assistant response
    ▼
Flask → JSON → Browser renders response
```

## Key Design Decisions & Best Practices

1. **Conversation history** — stored server-side in Flask sessions so the AI remembers context within a chat.
2. **System prompt** — gives the AI a consistent personality and instructions.
3. **History trimming** — caps at 50 messages to avoid exceeding token limits.
4. **Input validation** — rejects empty messages with a clear error.
5. **Error handling** — catches OpenAI API errors and returns friendly messages.
6. **Environment variables** — secrets are in `.env`, never hard-coded.
7. **Separation of concerns** — backend (Python) and frontend (HTML/JS) are cleanly separated.

## Customisation Ideas

- **Streaming responses**: Use `stream=True` in the OpenAI call + Server-Sent Events to show tokens as they arrive.
- **Database storage**: Replace Flask sessions with SQLite/PostgreSQL for persistent chat history.
- **Authentication**: Add user login to keep conversations private.
- **Multiple models**: Let users pick between gpt-4.1-mini and gpt-4.1 in the UI.
- **RAG (Retrieval-Augmented Generation)**: Connect a vector database to give the AI access to your own documents.
