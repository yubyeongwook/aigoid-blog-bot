import os
from dotenv import load_dotenv
load_dotenv()

print("ANTHROPIC_API_KEY present:", bool(os.getenv("ANTHROPIC_API_KEY")))
print("GEMINI_API_KEY present:", bool(os.getenv("GEMINI_API_KEY")))
print("PRIMARY_AI value:", os.getenv("PRIMARY_AI"))
