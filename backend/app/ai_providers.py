import os
from typing import Protocol


class AIProvider(Protocol):
    def generate(self, *, system: str, prompt: str) -> str: ...


class AIProviderError(RuntimeError):
    pass


class TemplateProvider:
    name = "template"

    def generate(self, *, system: str, prompt: str) -> str:
        return (
            "O provedor de IA ainda não está configurado. Esta resposta é apenas o fallback "
            "local do Tribunal Virtual e não representa análise jurídica real."
        )


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

    def generate(self, *, system: str, prompt: str) -> str:
        if not self.api_key:
            raise AIProviderError("GEMINI_API_KEY não configurada")

        try:
            from google import genai
        except ImportError as exc:
            raise AIProviderError("Dependência google-genai não instalada") from exc

        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model,
            contents=f"INSTRUÇÕES DO SISTEMA:\n{system}\n\nCASO:\n{prompt}",
        )
        text = getattr(response, "text", None)
        if not text:
            raise AIProviderError("Gemini retornou uma resposta vazia")
        return text


def get_provider() -> AIProvider:
    provider = os.getenv("AI_PROVIDER", "template").lower()
    if provider == "gemini":
        return GeminiProvider()
    return TemplateProvider()
