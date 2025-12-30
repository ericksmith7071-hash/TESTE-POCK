# TESTE-POCK

Este repositório contém o backend (FastAPI + Socket.IO) em `pocket_robot` e um frontend estático em `pocket_robot/frontend` além de um app Vite em `external_prisma_repo`.

Rápido (Docker):

1. Build e subir todos os serviços:

```bash
docker compose up --build -d
```

2. Acesse:

- Backend/API: http://localhost:8000
- Frontend (produção, nginx): http://localhost:8080

Desenvolvimento local:

- Backend (dev):

```bash
cd pocket_robot
python3 -m pip install -r requirements.txt
uvicorn pocket_robot.webapi.app:asgi_app --reload --host 0.0.0.0 --port 8000
```

- Frontend Vite (dev):

```bash
cd external_prisma_repo
npm install
npm run dev
```

Observações:

- Ajuste a variável de ambiente `POCKET_SSID` para conectar ao seu SSID real.
- Se `external_prisma_repo` for um repositório externo, considere convertê-lo em submódulo Git.
# TESTE-POCK
