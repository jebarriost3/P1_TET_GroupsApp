# Gateway Service

Servicio gateway para unificar el acceso a Auth, Groups y Messages.

## Ejecutar

```powershell
.venv\Scripts\activate
python gateway_service\manage.py runserver 8000
```

## Rutas principales

- `GET /`
- `GET /login/`
- `GET /register/`
- `GET /app/`
- `GET /health/`
- `GET /api/health/`
- `/api/auth/*` -> Auth Service
- `/api/groups/*` -> Group Service
- `/api/chat/*` -> Message Service
