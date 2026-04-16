# Group Service

Servicio independiente de grupos para GroupsApp.

## Ejecutar

```powershell
.venv\Scripts\activate
python group_service\manage.py runserver 8002
```

## Endpoints

- `GET /health/`
- `GET /groups/`
- `POST /groups/`
- `POST /groups/{group_id}/members/`
