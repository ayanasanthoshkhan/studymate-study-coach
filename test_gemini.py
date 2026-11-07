
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

model = "gemini-3.1-flash-lite"

for attempt in range(3):
    try:
        response = client.models.generate_content(
            model=model,
            contents="Hello! Introduce yourself in two sentences."
        )

        if not response.text:
            print("Gemini returned no text.")
            break

        print("Gemini response:")
        print(response.text)
        break

    except errors.ServerError as error:
        if error.code != 503:
            print(f"Server error: {error.code}")
            break

        if attempt == 2:
            print("Gemini is still busy after 3 attempts.")
            break

        delay = 2 ** (attempt + 1)
        print(f"Server busy. Retrying in {delay} seconds...")
        time.sleep(delay)

    except errors.APIError as error:
        print(f"API error: {error.code}")
        print(error.message)
        break

    except Exception as error:
        print(f"Connection error: {type(error).__name__}")
        break
