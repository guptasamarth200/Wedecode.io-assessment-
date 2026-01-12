import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Available models for this API key:\n")

for m in genai.list_models():
    print(m.name, "->", m.supported_generation_methods)
