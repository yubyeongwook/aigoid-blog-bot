import sys
import os
import requests
from dotenv import load_dotenv
load_dotenv()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Import the real anthropic package first
import anthropic
RealAnthropic = anthropic.Anthropic

class ContentBlock:
    def __init__(self, text):
        self.text = text
        self.type = "text"

class MessageResponse:
    def __init__(self, text):
        self.content = [ContentBlock(text)]

class AnthropicFallback:
    def __init__(self, api_key=None, **kwargs):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        try:
            self.real_client = RealAnthropic(api_key=self.api_key, **kwargs)
        except Exception:
            self.real_client = None

    @property
    def messages(self):
        return self

    def create(self, model, max_tokens, system, messages, tools=None):
        primary_ai = os.getenv("PRIMARY_AI", "claude").lower()
        if primary_ai == "gemini":
            order = ["gemini", "claude"]
        else:
            order = ["claude", "gemini"]

        last_error = None
        for provider in order:
            if provider == "claude":
                if not self.api_key:
                    last_error = "No ANTHROPIC_API_KEY found"
                    continue
                print(f"🤖 Claude API 호출 시도 ({model})...")
                try:
                    if self.real_client is None:
                        self.real_client = RealAnthropic(api_key=self.api_key)
                    resp = self.real_client.messages.create(
                        model=model,
                        max_tokens=max_tokens,
                        system=system,
                        messages=messages,
                        tools=tools
                    )
                    print("✅ Claude API 호출 성공")
                    return resp
                except Exception as e:
                    last_error = str(e)
                    print(f"⚠️ Claude API 호출 실패: {e}")
            elif provider == "gemini":
                gemini_key = os.getenv("GEMINI_API_KEY", "")
                if not gemini_key:
                    last_error = "No GEMINI_API_KEY found"
                    continue
                print("🤖 Gemini API 호출 시도...")
                gemini_model = "gemini-3.5-flash"
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={gemini_key}"
                
                user_text = ""
                for msg in messages:
                    user_text += f"\n\n{msg.get('content', '')}"
                combined_text = f"{system}\n\n{user_text}".strip()

                body = {
                    "contents": [{"parts": [{"text": combined_text}]}],
                    "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.3}
                }
                try:
                    res = requests.post(url, json=body, timeout=120)
                    if res.status_code == 200:
                        data = res.json()
                        candidates = data.get("candidates", [])
                        if not candidates:
                            last_error = "Gemini: No candidates returned"
                            continue
                        content = candidates[0].get("content", {})
                        parts = content.get("parts", [])
                        if not parts:
                            last_error = "Gemini: No content parts returned"
                            continue
                        text = parts[0].get("text", "")
                        print(f"✅ Gemini API 호출 성공 ({gemini_model})")
                        return MessageResponse(text)
                    else:
                        last_error = f"Gemini status code {res.status_code}: {res.text}"
                        print(f"⚠️ Gemini API 호출 실패: {last_error}")
                except Exception as e:
                    last_error = str(e)
                    print(f"⚠️ Gemini API 호출 실패: {e}")

        raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")

# Apply monkeypatch
anthropic.Anthropic = AnthropicFallback

# Test the monkeypatch
from anthropic import Anthropic
client = Anthropic()

print("Testing monkeypatch with PRIMARY_AI = gemini:")
os.environ["PRIMARY_AI"] = "gemini"
resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=100,
    system="You are a helpful assistant.",
    messages=[{"role": "user", "content": "Say 'Hello World' in one word"}]
)
print("Response:", resp.content[0].text)

print("\nTesting monkeypatch with PRIMARY_AI = claude (should fail Claude and fallback to Gemini):")
os.environ["PRIMARY_AI"] = "claude"
resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=100,
    system="You are a helpful assistant.",
    messages=[{"role": "user", "content": "Say 'Hello World' in one word"}]
)
print("Response:", resp.content[0].text)
