import os
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)
api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)

print("Dostępne modele Gemini dla Twojego klucza API:")
for model in client.models.list():
    if 'gemini' in model.name:
        print(f"- {model.name}")