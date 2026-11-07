
# StudyMate — Context-Aware AI Study Coach

A context-aware AI learning assistant built using Python,
FastAPI, Google Gemini, and Streamlit.

StudyMate supports multi-turn conversations, context-window
management, four interactive study modes, and API error handling.

## Features

- Real LLM integration using Google Gemini
- Multi-turn conversation memory
- Unique conversation IDs
- Last-10-message context truncation
- Four learning modes:
  - Explain
  - Quiz Me
  - Explain Like I'm 12
  - Socratic
- Custom system prompts for each mode
- Notebook-style Streamlit interface
- Live conversation memory statistics
- API timeout and error handling
- Environment-variable API key protection

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python |
| Backend | FastAPI |
| AI Model | Gemini 3.1 Flash-Lite |
| Frontend | Streamlit |
| Testing | Pytest |
| API SDK | Google Gen AI SDK |

## Architecture

User
  |
  v
Streamlit Frontend
  |
  v
FastAPI Backend
  |
  +-- Conversation Memory
  |      Last 10 messages
  |
  +-- Study Mode System Prompt
  |
  v
Google Gemini API
  |
  v
AI Response
  |
  v
Streamlit Chat Interface

## Conversation Memory

Each conversation has a unique ID.

The backend maintains conversation history using
Python dictionaries.

For every new message:

1. Retrieve the previous conversation history.
2. Keep the most recent 10 messages.
3. Append the current user message.
4. Send the context and selected system prompt to Gemini.
5. Save the user message and AI response after success.
6. Return updated memory statistics.

The history limit is based on message count, not tokens.

Older messages are removed when the limit is exceeded.
Conversation history resets when the backend restarts.

## Study Modes

### Explain
Provides clear, structured explanations with examples.

### Quiz Me
Asks questions and evaluates student responses.

### Explain Like I'm 12
Explains complex topics using simple language.

### Socratic
Uses guiding questions to encourage critical thinking.

## Installation

### 1. Clone the repository

git clone https://github.com/ayanasanthoshkhan/studymate-study-coach.git

cd studymate-study-coach

### 2. Create a virtual environment

python -m venv .venv

Windows PowerShell:

.\.venv\Scripts\Activate.ps1

### 3. Install dependencies

python -m pip install -r requirements.txt

### 4. Configure the API key

Create a `.env` file in the project root:

GEMINI_API_KEY=your_actual_api_key

Get an API key from Google AI Studio:

https://aistudio.google.com/apikey

Never commit the `.env` file.

### 5. Start the FastAPI backend

python -m uvicorn backend.main:app --reload

Backend:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

### 6. Start Streamlit

Open a second terminal:

python -m streamlit run frontend/app.py

Open:

http://localhost:8501

## API Endpoints

GET /
- Backend status

GET /modes
- List supported study modes

POST /chat
- Send a message and receive a Gemini response

Example request:

{
  "message": "Explain machine learning",
  "conversation_id": null,
  "mode": "Explain"
}

The response includes:
- conversation_id
- mode
- response
- memory statistics

## Testing

Run:

python -m pytest tests/ -v

The project includes 11 automated tests covering:

- API endpoints
- Study modes
- Request validation
- Multi-turn conversation handling
- Context truncation
- Mocked Gemini responses
- Rate-limit handling
- Server errors
- Timeouts

Automated tests use mocks and do not require
real Gemini API requests.

## Error Handling

The backend provides readable responses for:

- Invalid requests
- Unknown conversation IDs
- API rate limits
- Gemini service failures
- Network errors
- Request timeouts

## Limitations

- Memory is stored in RAM, not a database.
- Older context is discarded after 10 messages.
- Conversation history is lost after a server restart.
- Gemini API availability depends on provider quotas.

## Future Improvements

- Persistent conversation storage using SQLite
- Summarization of older messages
- Token-aware context management
- Saved study sessions
- Learning progress tracking

## Internship Assignment

This project demonstrates LLM API integration,
conversation history management, context truncation,
custom system prompts, error handling, and a
working frontend.
