import os
import sys
import json
import requests
import anthropic
from dotenv import load_dotenv
load_dotenv()

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
                print(f"[Claude] API call attempt ({model})...")
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
                    print("[Claude] API call success")
                    return resp
                except Exception as e:
                    last_error = str(e)
                    print(f"[Claude] API call failed: {e}")
            elif provider == "gemini":
                gemini_key = os.getenv("GEMINI_API_KEY", "")
                if not gemini_key:
                    last_error = "No GEMINI_API_KEY found"
                    continue
                print("[Gemini] API call attempt...")
                gemini_model = "gemini-3.5-flash"
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={gemini_key}"
                
                user_text = ""
                for msg in messages:
                    user_text += f"\n\n{msg.get('content', '')}"
                combined_text = f"{system}\n\n{user_text}".strip()

                body = {
                    "contents": [{"parts": [{"text": combined_text}]}],
                    "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.3}
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
                        print(f"[Gemini] API call success ({gemini_model})")
                        print("--- RAW GEMINI RESPONSE START ---")
                        print(text)
                        print("--- RAW GEMINI RESPONSE END ---")
                        print("Candidate details:", json.dumps(candidates[0], ensure_ascii=False, indent=2))
                        return MessageResponse(text)
                    else:
                        last_error = f"Gemini status code {res.status_code}: {res.text}"
                        print(f"[Gemini] API call failed: {last_error}")
                except Exception as e:
                    last_error = str(e)
                    print(f"[Gemini] API call failed: {e}")

        raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")

# Apply monkeypatch to anthropic package
anthropic.Anthropic = AnthropicFallback
