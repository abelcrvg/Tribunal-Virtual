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
- Persistência: SQLAlchemy, com PostgreSQL recomendado para produção.
- Orquestração: agentes especializados por papel e fase processual.

## Execução local

### Frontend

```bash
npm install
npm run dev
```

Defina `NEXT_PUBLIC_API_URL=http://localhost:8000` no ambiente do frontend.

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Deploy

O frontend está preparado para **Vercel** (`vercel.json`). O backend possui Dockerfile e configuração para **Railway** (`backend/railway.toml`).

No backend de produção, configure:

- `DATABASE_URL`
- `GEMINI_API_KEY` (opcional; sem ela o fallback local permanece disponível)
- `CORS_ORIGINS` com a URL do frontend publicado

No frontend, configure `NEXT_PUBLIC_API_URL` com a URL pública do backend.

## Status

O backend possui testes automatizados executados pelo GitHub Actions. O próximo marco é publicar frontend e API e realizar o primeiro teste funcional ponta a ponta.
