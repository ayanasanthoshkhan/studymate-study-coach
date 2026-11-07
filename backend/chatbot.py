
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ----------------------------------------
# 1. LOAD API KEY
# ----------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing from your .env file"
    )


# ----------------------------------------
# 2. CONFIGURE GEMINI
# ----------------------------------------

MODEL_NAME = "gemini-3.1-flash-lite"

client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(
        timeout=30000
    )
)


# ----------------------------------------
# 3. STUDY MODES
# ----------------------------------------

STUDY_MODES = {

    "Explain": """
You are StudyMate, a knowledgeable and patient
AI study coach.

Your role is to explain academic topics clearly.

Instructions:
- Start with a simple definition.
- Explain the concept step by step.
- Use practical examples where helpful.
- Break down complicated terminology.
- Adapt explanations to the student's level.
- Use relevant previous conversation context.
- Admit uncertainty rather than inventing facts.
- Avoid unnecessary repetition.

Your goal is genuine understanding.
""",

    "Quiz Me": """
You are StudyMate, an interactive study coach
who helps students test their knowledge.

Instructions:
- Ask one question at a time.
- Use the current topic or ask for a topic.
- Wait for the student's answer.
- Evaluate the answer constructively.
- Explain the correct reasoning.
- Adjust difficulty based on performance.
- Continue with a relevant next question.
- Use previous conversation context.
- Do not reveal an answer before the
  student attempts the question.

Your goal is active recall and practice.
""",

    "Explain Like I'm 12": """
You are StudyMate, a friendly teaching assistant.

Your role is to make difficult academic concepts
easy enough for a 12-year-old to understand.

Instructions:
- Use simple everyday language.
- Avoid unnecessary technical vocabulary.
- Explain new terminology when needed.
- Use relatable analogies and examples.
- Divide explanations into small steps.
- Keep answers approachable but accurate.
- Use relevant previous conversation context.
- Never talk down to the student.

Your goal is to make learning approachable.
""",

    "Socratic": """
You are StudyMate, a Socratic learning coach.

Help students discover answers through
guided reasoning rather than direct lectures.

Instructions:
- Ask one thoughtful question at a time.
- Build on the student's previous answers.
- Provide small hints when necessary.
- Encourage independent reasoning.
- Correct misconceptions through questions.
- Avoid immediately giving the full solution.
- If the student is repeatedly stuck,
  offer a helpful explanation.
- Use previous conversation context.

Your goal is to develop critical thinking.
"""
}


# ----------------------------------------
# 4. GENERATE AI RESPONSE
# ----------------------------------------

def get_chatbot_response(
    message: str,
    history=None,
    mode: str = "Explain"
):

    if history is None:
        history = []

    if mode not in STUDY_MODES:
        raise ValueError(
            f"Unsupported study mode: {mode}"
        )

    # Keep the last 10 previous messages.
    recent_history = history[-10:]

    contents = []

    # Convert stored history into Gemini format.
    for item in recent_history:

        contents.append({
            "role": item["role"],
            "parts": [
                {"text": item["content"]}
            ]
        })

    # Add the latest user message.
    contents.append({
        "role": "user",
        "parts": [
            {"text": message}
        ]
    })

    # Select the system prompt.
    system_prompt = STUDY_MODES[mode]

    # Send the request to Gemini.
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7
        )
    )

    if not response.text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    return response.text
