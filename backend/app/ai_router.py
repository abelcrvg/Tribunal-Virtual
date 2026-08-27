from .agent_registry import agent_for
from .ai_provider import AIProvider, get_provider
from .case_memory import get_case_memory
from .models import Process


def generate_for_role(process: Process, role: str, instruction: str, provider: AIProvider | None = None) -> dict:
    definition = agent_for(role)
    if definition is None:
        raise ValueError(f"Papel de IA não registrado: {role}")
    memory = get_case_memory(str(process.id)).context()
    prompt = (
        f"PROCESSO {process.number}\nÁREA: {process.area.value}\nAUTOR: {process.plaintiff}\nRÉU: {process.defendant}\n"
        f"FATOS: {process.facts}\nHISTÓRICO: {memory.get('events', [])[-20:]}\n\n{instruction}"
    )
    response = (provider or get_provider()).generate(system=definition.system_prompt, prompt=prompt)
    return {"role": role, "name": definition.display_name, "content": response.text, "provider": response.provider, "model": response.model}
