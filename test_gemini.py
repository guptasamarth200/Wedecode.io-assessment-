import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-flash-lite-latest")

resp = model.generate_content('Return valid JSON: {"status": "ok"}')

print(resp.text)
