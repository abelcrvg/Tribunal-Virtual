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


def get_provider() -> AIProvider:
    # A seleção de provedores ficará centralizada aqui. As chaves nunca devem chegar ao frontend.
    provider = os.getenv("AI_PROVIDER", "fallback").lower()
    if provider == "fallback":
        return LocalFallbackProvider()
    raise RuntimeError(f"Provedor de IA não suportado: {provider}")
