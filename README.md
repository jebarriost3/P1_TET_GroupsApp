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
