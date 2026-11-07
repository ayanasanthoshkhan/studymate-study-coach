
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google.genai import errors
import httpx

from backend.chatbot import (
    get_chatbot_response,
    STUDY_MODES
)

from backend.memory import (
    create_conversation,
    get_history,
    save_message,
    get_memory_info
)


# ----------------------------------------
# CREATE FASTAPI APPLICATION
# ----------------------------------------

app = FastAPI(
    title="StudyMate Study Coach API",
    description="Context-aware AI study assistant",
    version="2.0.0"
)


# ----------------------------------------
# REQUEST MODEL
# ----------------------------------------

class ChatRequest(BaseModel):

    message: str = Field(
        min_length=1,
        max_length=10000
    )

    conversation_id: str | None = None

    mode: str = "Explain"


# ----------------------------------------
# HOME ENDPOINT
# ----------------------------------------

@app.get("/")
def home():
    return {
        "message": "StudyMate Study Coach API is running!",
        "version": "2.0.0"
    }


# ----------------------------------------
# AVAILABLE STUDY MODES
# ----------------------------------------

@app.get("/modes")
def get_modes():
    return {
        "modes": list(STUDY_MODES.keys())
    }


# ----------------------------------------
# CHAT ENDPOINT
# ----------------------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    message = request.message.strip()

    # Validate user message
    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    # Validate selected study mode
    if request.mode not in STUDY_MODES:
        raise HTTPException(
            status_code=400,
            detail="Invalid study mode selected."
        )

    # ------------------------------------
    # GET OR CREATE CONVERSATION
    # ------------------------------------

    if request.conversation_id:

        conversation_id = request.conversation_id
        history = get_history(conversation_id)

        if history is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found."
            )

    else:

        conversation_id = create_conversation()
        history = []

    # ------------------------------------
    # GENERATE GEMINI RESPONSE
    # ------------------------------------

    try:

        reply = get_chatbot_response(
            message=message,
            history=history,
            mode=request.mode
        )

    # ------------------------------------
    # GEMINI API ERRORS
    # ------------------------------------

    except errors.APIError as error:

        if error.code == 429:
            raise HTTPException(
                status_code=429,
                detail="API rate limit reached. Please try later."
            )

        elif error.code in (408, 504):
            raise HTTPException(
                status_code=504,
                detail="The AI request timed out. Please try again."
            )

        elif error.code in (500, 502, 503):
            raise HTTPException(
                status_code=503,
                detail="The AI service is temporarily unavailable."
            )

        elif error.code in (401, 403):
            raise HTTPException(
                status_code=503,
                detail="The AI service is not configured correctly."
            )

        else:
            raise HTTPException(
                status_code=502,
                detail="The AI service could not process the request."
            )

    # ------------------------------------
    # TIMEOUT ERRORS
    # ------------------------------------

    except (TimeoutError, httpx.TimeoutException):
        raise HTTPException(
            status_code=504,
            detail="The AI request timed out. Please try again."
        )

    # ------------------------------------
    # NETWORK CONNECTION ERRORS
    # ------------------------------------

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Unable to reach the AI service."
        )

    # ------------------------------------
    # UNEXPECTED ERRORS
    # ------------------------------------

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An unexpected chatbot error occurred."
        )

    # ------------------------------------
    # SAVE SUCCESSFUL CONVERSATION
    # ------------------------------------

    save_message(
        conversation_id,
        "user",
        message
    )

    save_message(
        conversation_id,
        "model",
        reply
    )

    # ------------------------------------
    # FETCH REAL MEMORY INFORMATION
    # ------------------------------------

    memory_info = get_memory_info(
        conversation_id
    )

    # ------------------------------------
    # RETURN RESPONSE
    # ------------------------------------

    return {
        "conversation_id": conversation_id,
        "mode": request.mode,
        "response": reply,
        "memory": memory_info
    }
