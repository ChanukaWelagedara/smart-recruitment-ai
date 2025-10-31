from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing in your environment variables.")

print(f"Using API key: {api_key[:10]}... (length={len(api_key)})")

client = Groq(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="llama3-70b-8192",  # Full model name
        messages=[{"role": "user", "content": "Hello Groq!"}],
        max_tokens=10,
    )
    print("Success:", response.choices[0].message.content)
except Exception as e:
    print("Error:", e)
