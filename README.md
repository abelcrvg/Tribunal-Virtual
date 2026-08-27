# Tribunal Virtual

Simulador educacional de processos e audiências inspirado no processo judicial brasileiro.

## Objetivo

O projeto cria uma experiência de tribunal interativa na qual o usuário escolhe um papel, participa de uma audiência por chat e interage com personagens fictícios assistidos por IA.

## Fluxo

1. Criar processo e informar os fatos.
2. Escolher o papel do usuário.
3. Abrir a sala de julgamento.
4. Acompanhar juiz, partes, testemunhas, perito, Ministério Público e, quando aplicável, jurados.
5. Debater livremente respeitando a ordem processual.
6. Registrar manifestações relevantes no histórico.
7. Avançar pelas fases da audiência.
8. Produzir decisão/sentença.
9. Permitir recursos e simular instâncias superiores.

## Princípios da simulação

- Personagens têm nomes fictícios.
- O sistema deve diferenciar alegações, fatos e provas.
- A IA não deve inventar documentos, depoimentos ou acontecimentos como se fossem fatos dos autos.
- Intervenções fora da vez podem ser admitidas quando apresentarem pertinência relevante.
- Intervenções abusivas ou sem pertinência podem gerar advertência judicial.
- O resultado é educacional e não constitui aconselhamento jurídico.

## Arquitetura

- Frontend: Next.js / React / TypeScript.
- Backend: FastAPI / Python.
- Persistência: SQLAlchemy, com evolução planejada para PostgreSQL em produção.
- Orquestração: agentes especializados por papel e fase processual.

## Execução local

Consulte os arquivos de configuração do frontend e backend para instalar as dependências e definir `NEXT_PUBLIC_API_URL` apontando para a API.

## Próximos marcos

- persistência completa da sessão de audiência;
- geração de personagens e casos;
- integração de provedores de IA gratuitos;
- documentos e provas;
- sentença fundamentada;
- recursos e julgamento colegiado;
- testes automatizados e deploy.
