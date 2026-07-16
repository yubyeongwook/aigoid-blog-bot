import os
import sys
import json
import anthropic
from dotenv import load_dotenv
load_dotenv()

RealAnthropic = anthropic.Anthropic

# ────────────────────────────────────────────────────────────
#  Claude Sonnet 4.6 전용 클라이언트 (Gemini 폴백 제거)
#  → 실패 시 예외를 raise하여 에러 내용이 포스트로 발행되는
#    사고를 원천 차단합니다.
# ────────────────────────────────────────────────────────────

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
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY가 설정되지 않았습니다. 발행을 중단합니다.")

        print(f"[Claude Sonnet 4.6] API call attempt ({model})...")
        try:
            if self.real_client is None:
                self.real_client = RealAnthropic(api_key=self.api_key)
            resp = self.real_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
                **({"tools": tools} if tools else {})
            )
            print("[Claude Sonnet 4.6] API call success")
            return resp
        except Exception as e:
            print(f"[Claude Sonnet 4.6] API call failed: {e}")
            # 폴백 없이 예외를 그대로 raise → 발행 차단
            raise

# Apply monkeypatch to anthropic package
anthropic.Anthropic = AnthropicFallback
