from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_LLM_MODEL = "gpt-4.1-mini"
DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"


class OpenAIResponsesLLM:
    """Small callable client for the OpenAI Responses API."""

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_LLM_MODEL,
        base_url: str = DEFAULT_OPENAI_BASE_URL,
        timeout: float = 45.0,
    ) -> None:
        if not api_key.strip():
            raise ValueError("An OpenAI API key is required")
        self.api_key = api_key.strip()
        self.model = model.strip() or DEFAULT_LLM_MODEL
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @classmethod
    def from_env(cls) -> "OpenAIResponsesLLM":
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API")
        if not api_key:
            raise RuntimeError("Set LLM_API or OPENAI_API_KEY in .env")
        model = os.getenv("LLM_MODEL") or os.getenv("OPENAI_CHAT_MODEL") or DEFAULT_LLM_MODEL
        base_url = os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL") or DEFAULT_OPENAI_BASE_URL
        return cls(api_key=api_key, model=model, base_url=base_url)

    def __call__(self, prompt: str) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "input": prompt,
                "max_output_tokens": 500,
            }
        ).encode("utf-8")
        request = Request(
            f"{self.base_url}/responses",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            detail = self._read_error(error)
            raise RuntimeError(f"LLM API request failed ({error.code}): {detail}") from error
        except URLError as error:
            raise RuntimeError(f"Cannot connect to the LLM API: {error.reason}") from error

        text_parts = []
        for item in data.get("output", []):
            if item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    text_parts.append(content["text"])

        answer = "\n".join(text_parts).strip()
        if not answer:
            raise RuntimeError("The LLM API returned no text output")
        return answer

    def _read_error(self, error: HTTPError) -> str:
        try:
            payload = json.loads(error.read().decode("utf-8"))
            detail = payload.get("error", {}).get("message", "Unknown API error")
        except (json.JSONDecodeError, UnicodeDecodeError):
            detail = "Unknown API error"
        return str(detail).replace(self.api_key, "[redacted]")[:300]
