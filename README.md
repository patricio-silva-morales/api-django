# API REST del Help Desk

Backend de prácticas para el proyecto Angular. El archivo db.sqlite3 ya contiene 10.000 tickets y 1.000 fichas ficticias de usuario. Conserva los 60 tickets de la versión revisada, incluidos sus identificadores, y anonimiza nombres y correos de las tres fichas originales. Las fichas de usuario y las cuentas de acceso son entidades separadas.

## Ejecutar en Windows (CMD)

Desde la carpeta que contiene manage.py, con Python 3.10 o superior:

```cmd
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
```

El comando opcional `python manage.py cargar_demo` repone los registros de muestra ausentes. Usa claves estables y respeta filas existentes. Para generar otra cantidad en una base limpia, ejecuta por ejemplo `python manage.py cargar_demo --tickets 20000 --usuarios 2000`. Reducir los parámetros en una base ya poblada conserva los registros existentes.

### Prueba local con el Angular del curso

Detén JSON Server antes de reutilizar el puerto 3000. En CMD:

```cmd
set "HELPDESK_LOCAL_ABIERTO=1"
python manage.py runserver 127.0.0.1:3000
```

Este modo es para pruebas en tu equipo, con datos ficticios. Usa el modo con cuentas para compartir la API.

`GET http://localhost:3000/tickets` devuelve un arreglo JSON. Los detalles se consultan con `GET /tickets/1`. Las URL del cliente Angular observado siguen funcionando, incluidas `/usuario` y `/usuarios`.

## Contrato

| Recurso | Listado / creación | Detalle / reemplazo / edición parcial / eliminación |
|---|---|---|
| Tickets | GET y POST /tickets | GET, PUT, PATCH y DELETE /tickets/{id} |
| Usuarios | GET y POST /usuarios | GET, PUT, PATCH y DELETE /usuarios/{id} |

Los recursos usan id de texto. Las colecciones devuelven arreglos sin envoltorio para que el dashboard pueda agregar toda la colección. Ejemplo de creación por POST /tickets:

```json
{
  "asunto": "Sin acceso a la VPN",
  "descripcion": "El equipo solicita revisar la conexión.",
  "estado": "Abierto",
  "prioridad": "Alta",
  "fechaCreacion": "2026-11-16"
}
```

Estados válidos: Abierto, En proceso y Cerrado. Prioridades válidas: Baja, Media y Alta. Roles de las fichas: Usuario, Soporte y Administrador. Campos de la ficha: id, nombre, email, rol. PUT envía el objeto completo y PATCH acepta campos parciales. El servidor asigna id al crear.

Puedes probar `GET /tickets?estado=Abierto&prioridad=Alta&ordering=-fechaCreacion` o `GET /tickets?search=VPN`.

## Compartir con el curso

El modo normal exige una credencial Bearer. Crea las cuentas necesarias. El comando solicita la contraseña sin mostrarla:

```cmd
set "HELPDESK_LOCAL_ABIERTO="
python manage.py crear_cuenta alumno01 Soporte
python manage.py crear_cuenta lector01 Usuario
python manage.py crear_cuenta docente Administrador
python manage.py runserver 127.0.0.1:8000
```

| Perfil | Tickets | Fichas de usuario |
|---|---|---|
| Usuario | Lectura | Lectura |
| Soporte | Lectura, creación y edición | Lectura |
| Administrador | CRUD | CRUD |

En VS Code reenvía solo el puerto HTTP 8000. Copia la URL HTTPS asignada y añade su hostname exacto antes de reiniciar el servidor. Ejemplo en CMD, sustituyendo el host:

```cmd
set "HELPDESK_HOSTS=localhost,127.0.0.1,HOST-DEL-TUNEL"
python manage.py runserver 127.0.0.1:8000
```

En Postman envía POST a /auth/token con un cuerpo JSON que tenga username y password. Copia token de la respuesta. En /tickets y /usuarios, utiliza Authorization de tipo Bearer Token. Una petición sin credencial recibe 401. Una cuenta autenticada sin permiso de escritura recibe 403.

Para usar Angular con el túnel, sustituye localhost:3000 por la URL HTTPS en ambos servicios y ajusta la comparación de origen en el interceptor. El inicio de sesión de demostración deberá llamar a /auth/token y guardar el token retornado. Los roles que aparecen en la interfaz deben corresponder a las cuentas entregadas. El servidor determina los permisos por los grupos de cada cuenta. La integración de ese login en el frontend es un paso adicional. CORS permite los orígenes locales del cliente Angular en el puerto 4200. Para otros, define HELPDESK_CORS como una lista separada por comas de los orígenes exactos.

Para la demostración, conserva el puerto y el proceso activos. Todos los alumnos escribirán en la misma base. Asigna tickets distintos al practicar edición y reserva los borrados al perfil docente. El servidor de desarrollo es para esta práctica. SQLite sirve esos miles de filas y serializa las escrituras concurrentes.
