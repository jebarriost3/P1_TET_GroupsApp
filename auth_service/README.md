# Auth Service

Servicio independiente de autenticacion para GroupsApp.

## Ejecutar

```powershell
.venv\Scripts\activate
python auth_service\manage.py runserver 8001
```

## Endpoints

- `GET /health/`
- `POST /auth/register/`
- `POST /auth/login/`
- `POST /auth/refresh/`
- `GET /auth/me/`
