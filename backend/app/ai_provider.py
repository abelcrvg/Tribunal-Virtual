from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AIResponse:
    text: str
    provider: str
    model: str


class AIProvider:
    def generate(self, *, system: str, prompt: str) -> AIResponse:
        raise NotImplementedError


class LocalFallbackProvider(AIProvider):
    """Deterministic fallback used when no external provider is configured."""

    def generate(self, *, system: str, prompt: str) -> AIResponse:
        return AIResponse(
            text=(
                "A análise por IA ainda não está configurada neste ambiente.\n\n"
                "O motor recebeu o caso corretamente e está pronto para encaminhá-lo a um "
                "provedor de IA. Nenhuma lei, precedente, fato ou prova foi inventada pelo fallback."
            ),
            provider="fallback",
            model="deterministic",
        )


class GeminiProvider(AIProvider):
    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY não configurada")

    def generate(self, *, system: str, prompt: str) -> AIResponse:
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError("Instale a dependência google-genai para usar o Gemini") from exc

        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model,
            contents=f"INSTRUÇÕES DO SISTEMA:\n{system}\n\nCASO:\n{prompt}",
        )
        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("O Gemini retornou uma resposta vazia")
        return AIResponse(text=text, provider="gemini", model=self.model)


def get_provider() -> AIProvider:
    provider = os.getenv("AI_PROVIDER", "fallback").lower()
    if provider == "gemini":
        return GeminiProvider()
    if provider == "fallback":
        return LocalFallbackProvider()
    raise RuntimeError(f"Provedor de IA não suportado: {provider}")
