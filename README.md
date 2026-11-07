# StudyMate — Context-Aware AI Study Coach

A context-aware AI learning assistant built with **Python, FastAPI, Google Gemini, and Streamlit**.

StudyMate is an interactive study coach designed to help students understand complex concepts, test their knowledge, and develop critical-thinking skills. It supports multi-turn conversations, context-window management, four learning modes, and user-friendly API error handling.

## Features

- **Real LLM Integration:** Generates responses using the Google Gemini API.
- **Multi-Turn Conversation Memory:** Maintains previous messages using unique conversation IDs.
- **Context-Window Management:** Implements last-10-message truncation to limit conversation history.
- **Four Interactive Study Modes:**
  - **Explain:** Provides structured explanations with practical examples.
  - **Quiz Me:** Asks questions and evaluates student answers.
  - **Explain Like I'm 12:** Simplifies difficult concepts using everyday language.
  - **Socratic:** Guides students through questions to encourage independent reasoning.
- **Custom System Prompts:** Each mode uses a different set of instructions.
- **Notebook-Style Interface:** A clean Streamlit learning workspace.
- **Conversation Memory Statistics:** Displays retained and truncated message counts.
- **Error Handling:** Handles API failures, rate limits, invalid requests, and timeouts.
- **Secure API Configuration:** Loads credentials from environment variables.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| LLM Provider | Google Gemini |
| Model | Gemini 3.1 Flash-Lite |
| Frontend | Streamlit |
| HTTP Clients | Requests, HTTPX |
| Testing | Pytest |
| API SDK | Google Gen AI SDK |
| Environment Configuration | python-dotenv |

## System Architecture

```text
              USER
               |
               v
       Streamlit Frontend
               |
               | HTTP POST /chat
               v
        FastAPI Backend
               |
       +-------+--------+
       |                |
       v                v
 Conversation       Study Mode
    Memory          Selection
 (Last 10 msgs)         |
       |                v
       |          System Prompt
       |                |
       +-------+--------+
               |
               v
       Google Gemini API
               |
               v
       Generated Response
               |
               v
      Update Conversation
           Memory
               |
               v
       Streamlit Frontend
```

### Application Workflow

1. The user selects a study mode and submits a question through Streamlit.
2. The frontend sends the message, conversation ID, and selected mode to FastAPI.
3. The backend retrieves the recent conversation history.
4. The selected study mode determines the system prompt.
5. Gemini generates a response using the supplied context.
6. After successful generation, the backend saves the user message and AI response.
7. The backend returns the response, conversation ID, and updated memory statistics.
8. Streamlit displays the response and conversation details.

## Conversation Memory and Context Management

StudyMate implements a **last-N-message truncation strategy**, with `MAX_HISTORY = 10`.

Each conversation is identified by a unique UUID, and its history is maintained separately using Python dictionaries.

### How It Works

1. Retrieve the history associated with the conversation ID.
2. Select the most recent 10 stored messages.
3. Append the user's current message to the model request.
4. Send the conversation context and selected system instruction to Gemini.
5. After successful generation, save the new user message and model response.
6. Remove older stored messages when the history exceeds 10.
7. Return updated memory statistics to the frontend.

### Memory Information

The application tracks:

- Retained conversation messages
- Maximum stored history
- Total messages processed
- Number of truncated messages
- Whether truncation has occurred

**Note:** The context strategy limits the number of stored conversation messages, not the exact number of tokens. When the history is full, a request can include 10 previous messages plus the current user message and system instruction.

The full visible chat may contain older messages that are no longer included in Gemini's active context.

Conversation history is currently stored in memory and is reset when the backend restarts.

## Study Modes

### 1. Explain

Provides beginner-friendly explanations with structured steps and real-world examples.

### 2. Quiz Me

Acts as an interactive tutor by asking one question at a time, checking answers, and giving constructive feedback.

### 3. Explain Like I'm 12

Uses simple vocabulary, analogies, and relatable examples to make complex topics easier to understand.

### 4. Socratic

Encourages critical thinking by asking guiding questions rather than immediately providing complete solutions.

Users can switch modes without clearing the current conversation. The selected mode determines the system instructions used for subsequent responses.

## Project Structure

```text
studymate-study-coach/
│
├── backend/
│   ├── main.py
│   ├── chatbot.py
│   └── memory.py
│
├── frontend/
│   └── app.py
│
├── tests/
│   └── test_backend.py
│
├── .streamlit/
│   └── config.toml
│
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── test_gemini.py
```

### File Descriptions

| File | Responsibility |
|---|---|
| `backend/main.py` | FastAPI endpoints, request validation, and error handling |
| `backend/chatbot.py` | Gemini API integration and study-mode system prompts |
| `backend/memory.py` | Conversation IDs, memory storage, and truncation |
| `frontend/app.py` | Streamlit chatbot interface |
| `.streamlit/config.toml` | Notebook-inspired application theme |
| `tests/test_backend.py` | Automated backend tests |
| `test_gemini.py` | Gemini API connectivity test |
| `.env.example` | Safe environment-variable template |
| `requirements.txt` | Python dependencies |

## Installation and Setup

### Prerequisites

- Python 3.11 or newer
- Git
- A Google Gemini API key
- An internet connection

### 1. Clone the Repository

```bash
git clone https://github.com/ayanasanthoshkhan/studymate-study-coach.git
cd studymate-study-coach
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the Gemini API Key

Obtain an API key from [Google AI Studio](https://aistudio.google.com/apikey).

Create a `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your_actual_api_key_here
```

Replace the placeholder with your own API key.

**Security:** The `.env` file is excluded through `.gitignore`. Never commit API keys or other credentials to GitHub.

Gemini API access, free-tier availability, and quotas depend on the selected model and Google Cloud project.

### 5. Start the FastAPI Backend

Run from the project root:

```bash
python -m uvicorn backend.main:app --reload
```

Backend URL: http://127.0.0.1:8000

Interactive API documentation: http://127.0.0.1:8000/docs

### 6. Start the Streamlit Frontend

Open a second terminal, activate the same virtual environment, and run:

```bash
python -m streamlit run frontend/app.py
```

Open the application at:

http://localhost:8501

Both the FastAPI server and Streamlit application must be running to use the chatbot locally.

## API Documentation

### GET `/`

Returns backend status information.

### GET `/modes`

Returns the available study modes.

### POST `/chat`

Accepts a user message, selected study mode, and optional conversation ID.

**Example request:**

```json
{
  "message": "Explain supervised learning.",
  "conversation_id": null,
  "mode": "Explain"
}
```

**Example response structure:**

```json
{
  "conversation_id": "generated-uuid",
  "mode": "Explain",
  "response": "Supervised learning is a machine learning approach...",
  "memory": {
    "retained_messages": 2,
    "max_messages": 10,
    "total_messages": 2,
    "truncated_messages": 0,
    "truncation_active": false
  }
}
```

The conversation ID returned by the first successful request must be reused in subsequent requests to maintain conversational context.

## Testing

The project includes **11 automated tests** implemented using Pytest.

Run all tests from the project root:

```bash
python -m pytest tests/ -v
```

### Test Coverage

The automated tests cover:

- Backend status endpoint
- Available study modes
- Invalid study-mode validation
- Last-10-message memory truncation
- Successful chatbot responses using mocks
- Empty-message validation
- Unknown conversation IDs
- Gemini API rate-limit responses
- Gemini service-unavailable responses
- Python timeout handling
- HTTP transport timeout handling

**Test result:** 11 tests passed during local development.

Mocked tests do not consume real Gemini API quota.

### Manual Multi-Turn Conversation Test

A five-turn conversation was performed through the Streamlit interface to verify conversational context.

**Example test sequence:**

1. My name is Alex.
2. I'm studying data science.
3. Explain supervised learning.
4. Give me a real-world example.
5. What is my name, what am I studying, and what topic were we discussing?

**Observed result:** StudyMate correctly identified the name as Alex, the subject as Data Science, and the discussion topic as Supervised Learning.

## Error Handling

StudyMate provides controlled, user-friendly error responses for common failure scenarios.

| Scenario | Handling |
|---|---|
| Invalid study mode | HTTP 400 |
| Unknown conversation ID | HTTP 404 |
| API rate limit | HTTP 429 |
| Gemini service unavailable | HTTP 503 |
| API or HTTP transport timeout | HTTP 504 |
| Unexpected backend error | HTTP 500 |
| Frontend cannot reach backend | Readable connection-error message |

The application avoids intentionally exposing API keys or internal exception details through user-facing errors.

## Limitations

- Conversation histories are stored in RAM rather than a database.
- The last-10-message strategy can discard older important details.
- Memory resets when the backend restarts.
- Context is limited by message count, not an exact token budget.
- The application requires an internet connection and valid Gemini API access.
- Quiz mode provides interactive question-and-answer practice but does not implement a dedicated scoring system.

## Future Improvements

- Persistent conversation storage using SQLite
- Summarization of older conversation history
- Token-aware context budgeting
- Multiple saved study sessions
- Quiz performance tracking
- Improved automated integration testing
- Optional deployment for online access

## Internship Assignment

StudyMate was developed to demonstrate the core requirements of an LLM chatbot engineering assessment:

- Real LLM API integration
- Working backend endpoint
- Multi-turn conversation history
- Context-window management
- Custom system instructions
- API error and timeout handling
- Secure environment-variable configuration
- Functional end-to-end user interface

The project emphasizes conversational context management, backend reliability, and practical LLM application development.