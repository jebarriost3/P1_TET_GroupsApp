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
- Group gRPC: `127.0.0.1:50051`
- RabbitMQ Management: `http://127.0.0.1:15672`
- MongoDB: `127.0.0.1:27017`
