# File Service

Servicio independiente de archivos para GroupsApp.

## Ejecutar

```powershell
.venv\Scripts\activate
python file_service\manage.py migrate
python file_service\manage.py runserver 8004
```

## Endpoints

- `GET /health/`
- `POST /files/upload/`
- `GET /files/{id}/`

## Nota

Esta primera version usa almacenamiento local desacoplado y deja configuracion preparada para evolucionar a S3.
