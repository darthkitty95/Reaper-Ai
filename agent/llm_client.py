import os
import openai

class LLMClient:
    def __init__(self, provider="openai", model="gpt-4o-mini"):
        self.provider = provider
        self.model = model
        if provider == "openai":
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise RuntimeError("OPENAI_API_KEY not set")
            openai.api_key = key

    def suggest_fix(self, prompt: str):
        try:
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are a helpful code assistant."},
                          {"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.0,
            )
            text = resp["choices"][0]["message"]["content"]
            return None if not text or "NO_PATCH" in text else text
        except Exception as e:
            print(f"[llm] error: {e}")
            return None
