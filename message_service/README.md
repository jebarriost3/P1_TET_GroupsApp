# Message Service

Servicio independiente de mensajeria para GroupsApp.

## Ejecutar

```powershell
.venv\Scripts\activate
python message_service\manage.py runserver 8003
```

## Endpoints

- `GET /health/`
- `GET /groups/{group_id}/messages/`
- `POST /groups/{group_id}/messages/`
