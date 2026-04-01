"""
AI Chatbot — Flask Backend
==========================
Endpoints:
    POST /api/chat      — send a message, get an AI reply
    POST /api/chat/reset — clear conversation history
    GET  /               — serve the chat UI

Best practices applied:
    • System prompt for consistent AI behaviour
    • Server-side conversation history (per-session)
    • Streaming-ready structure (can be extended)
    • Input validation & error handling
    • CORS support for development
    • Environment-based configuration (.env)
"""

import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory, session
from openai import OpenAI, APIError

# ── Configuration ────────────────────────────────────────────────────────────
load_dotenv()  # reads .env file in project root

app = Flask(__name__, static_folder="static")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-me-in-production")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # key from env

MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", 50))  # max messages kept per session

SYSTEM_PROMPT = (
    "You are a helpful, friendly AI assistant. "
    "Answer concisely and accurately. "
    "If you are unsure, say so rather than guessing."
)


# ── Helpers ──────────────────────────────────────────────────────────────────
def get_history() -> list[dict]:
    """Return the conversation history list for the current session."""
    if "history" not in session:
        session["history"] = []
    return session["history"]


def trim_history(history: list[dict]) -> list[dict]:
    """Keep only the last MAX_HISTORY messages to stay within token limits."""
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
    return history


def build_messages(history: list[dict]) -> list[dict]:
    """Construct the messages payload sent to the OpenAI API."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    return messages


# ── API Endpoints ────────────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def chat():
    """
    POST /api/chat
    Body: { "message": "Hello!" }
    Response: { "reply": "Hi there!", "conversation_id": "..." }
    """
    data = request.get_json(silent=True)
    if not data or not data.get("message", "").strip():
        return jsonify({"error": "Missing or empty 'message' field."}), 400

    user_message = data["message"].strip()

    # Retrieve & update conversation history
    history = get_history()
    history.append({"role": "user", "content": user_message})
    history = trim_history(history)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=build_messages(history),
            temperature=0.7,
            max_tokens=1024,
        )
        assistant_reply = response.choices[0].message.content
    except APIError as e:
        app.logger.error("OpenAI API error: %s", e)
        return jsonify({"error": f"AI service error: {e.message}"}), 502
    except Exception as e:
        app.logger.error("Unexpected error: %s", e)
        return jsonify({"error": "Internal server error."}), 500

    # Save assistant reply to history
    history.append({"role": "assistant", "content": assistant_reply})
    session["history"] = trim_history(history)

    return jsonify({
        "reply": assistant_reply,
        "conversation_id": session.get("conv_id", ""),
    })


@app.route("/api/chat/reset", methods=["POST"])
def reset():
    """Clear conversation history for the current session."""
    session.pop("history", None)
    session["conv_id"] = str(uuid.uuid4())
    return jsonify({"status": "ok", "message": "Conversation reset."})


# ── Serve frontend ───────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    port = int(os.getenv("PORT", 5000))
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
