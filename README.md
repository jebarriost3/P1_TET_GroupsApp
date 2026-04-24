# P1_TET_GroupsApp

## Servicios

### Monolito principal

```powershell
.venv\Scripts\activate
python manage.py runserver
```

### Auth Service

```powershell
.venv\Scripts\activate
python auth_service\manage.py runserver 8001
```

### Group Service

```powershell
.venv\Scripts\activate
python group_service\manage.py runserver 8002
```

### Group Service gRPC

```powershell
.venv\Scripts\activate
python group_service\manage.py grpc_server
```

### Message Service

```powershell
.venv\Scripts\activate
python message_service\manage.py runserver 8003
```

### Gateway Service

```powershell
.venv\Scripts\activate
python gateway_service\manage.py runserver 8000
```

### File Service

```powershell
.venv\Scripts\activate
python file_service\manage.py migrate
python file_service\manage.py runserver 8004
```

### Notification Service

```powershell
.venv\Scripts\activate
python notification_service\manage.py migrate
python notification_service\manage.py runserver 8005
```

### Notification Worker

```powershell
.venv\Scripts\activate
python notification_service\manage.py consume_events
```

## Flujo de archivos en mensajes

1. Subir archivo por gateway a `POST /api/files/upload/`
2. Tomar el `id` devuelto por `File Service`
3. Crear mensaje por gateway con `attachment_id`

Ejemplo:

```json
{
  "content": "mensaje con adjunto",
  "attachment_id": 1
}
```

## Docker Compose

Levanta los servicios principales de la arquitectura distribuida:

```powershell
docker compose up --build
```

Servicios expuestos:

- Gateway: `http://127.0.0.1:8000`
- Auth Service: `http://127.0.0.1:8001`
- Group Service: `http://127.0.0.1:8002`
- Message Service: `http://127.0.0.1:8003`
- File Service: `http://127.0.0.1:8004`
- Notification Service: `http://127.0.0.1:8005`
- Group gRPC: `127.0.0.1:50051`
- RabbitMQ Management: `http://127.0.0.1:15672`
- MongoDB: `127.0.0.1:27017`

Notas de configuracion:

- `MESSAGE_PERSISTENCE_BACKEND=postgres` para desarrollo local con PostgreSQL
- `MESSAGE_PERSISTENCE_BACKEND=mongo` para mensajeria sobre MongoDB
- `GET /api/notifications/` lista notificaciones del usuario autenticado
- `POST /api/notifications/<id>/read/` marca una notificacion como leida
