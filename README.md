# GroupsApp – Aplicación de Chat en Grupos

## Descripción

GroupsApp es una aplicación web que permite a los usuarios crear grupos y comunicarse mediante mensajes dentro de dichos grupos. La aplicación implementa autenticación de usuarios, gestión de grupos y envío de mensajes dentro de cada grupo.

Este proyecto corresponde al desarrollo de una **aplicación monolítica** desplegada en **AWS EC2**, utilizando **Django** como framework backend y **Nginx + Gunicorn** como servidor de producción.

---

# Funcionalidades

La aplicación permite:

- Registro de nuevos usuarios
- Inicio de sesión
- Creación de grupos
- Agregar miembros a grupos
- Envío de mensajes dentro de los grupos
- Visualización de conversaciones por grupo

---

# Arquitectura del sistema

El sistema sigue una **arquitectura monolítica**, donde todos los componentes de la aplicación se ejecutan en un único servidor.

## Componentes

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Django
- **Servidor de aplicaciones:** Gunicorn
- **Servidor web / Reverse Proxy:** Nginx
- **Base de datos:** SQLite
- **Infraestructura:** AWS EC2 (Ubuntu)

---

# Despliegue en AWS

La aplicación fue desplegada en una instancia **EC2** utilizando la siguiente arquitectura:
```bash
Usuario (Navegador)
│
▼
Nginx
│
▼
Gunicorn
│
▼
Django
│
▼
SQLite
```


Nginx recibe las peticiones HTTP y las redirige a Gunicorn, que ejecuta la aplicación Django.

---

# Acceso a la aplicación

La aplicación se encuentra desplegada en:
http://3.236.123.244

---

# Tecnologías utilizadas

- Python
- Django
- Gunicorn
- Nginx
- HTML
- CSS
- JavaScript
- AWS EC2
- SQLite

---

# Ejecución del proyecto en local

### 1. Clonar el repositorio

```bash
git clone https://github.com/jebarriost3/P1_TET_GroupsApp.git
cd P1_TET_GroupsApp
```

### 2. Crear entorno virtual
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```
### 4. Aplicar migraciones 
```bash
python manage.py migrate
```

### 5. Ejecutar el servidor
```bash
python manage.py runserver
```

# Autores 
## **Juan Esteban Barrios Tovar**
## **Alejandro García** 


