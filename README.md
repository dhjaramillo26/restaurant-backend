
# API de Reservas de Restaurantes

Sistema backend para la administración de restaurantes y la gestión de reservas de mesas.  
Permite crear, consultar, actualizar y eliminar restaurantes y reservas, asegurando restricciones de cupo diario por restaurante (máximo 15 reservas) y un tope global de 20 reservas diarias entre todos los restaurantes.

## Requisitos

- Python 3.10 o superior
- `pip` para instalar las dependencias

## Instalación

1. Clona el repositorio y entra en la carpeta del proyecto:

   ```bash
   git clone <tu-url> && cd restaurant-backend
   ```

2. Crea un entorno virtual (opcional pero recomendado) y actívalo:

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
   ```

3. Instala las dependencias del proyecto:

   ```bash
   pip install -r requirements.txt
   ```

## Configuración

Por defecto, la aplicación utiliza una base de datos SQLite llamada `reservas.db`.  
Si deseas usar otra base de datos (por ejemplo, PostgreSQL o MySQL), define la variable de entorno `DATABASE_URL` antes de ejecutar la aplicación:

```bash
export DATABASE_URL='postgresql://usuario:contraseña@localhost:5432/mi_basededatos'
```

## Migraciones de Base de Datos

El proyecto utiliza migraciones para crear y actualizar las tablas de la base de datos.

- Si es la **primera vez** que ejecutas el proyecto:

  ```bash
  flask db init
  flask db migrate -m "Migración inicial"
  flask db upgrade
  ```

- Si ya existe la carpeta de migraciones:

  ```bash
  flask db upgrade
  ```

**Nota:** Asegúrate de que la variable `SQLALCHEMY_DATABASE_URI` esté correctamente configurada en tu archivo `.env` o en las variables de entorno.

## Ejecución

Para iniciar la API ejecuta:

```bash
python manage.py
```

Por defecto estará disponible en [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Endpoints

### Raíz

- **GET /**  
  Devuelve un mensaje de prueba para comprobar que la API está activa.
  - **Ejemplo de respuesta:**
    ```json
    {"message": "API de reservas activa"}
    ```

### Restaurantes

- **GET /restaurants**  
  Obtiene la lista de restaurantes.
  - Parámetros opcionales:
    - `letra`: filtra por letra inicial del nombre (ej: `letra=A`)
    - `ciudad`: filtra por ciudad (ej: `ciudad=Bogotá`)
  - **Ejemplo de respuesta:**
    ```json
    [
      {
        "id": 1,
        "name": "Arepa House",
        "description": "Comida típica",
        "address": "Calle 123",
        "city": "Bogotá",
        "image_url": "http://..."
      }
    ]
    ```

- **POST /restaurants**  
  Crea un nuevo restaurante.
  - **Cuerpo JSON de ejemplo:**
    ```json
    {
      "name": "Mi Restaurante",
      "description": "Comida típica",
      "address": "Calle 123",
      "city": "Bogotá",
      "image_url": "http://..."
    }
    ```
  - **Respuesta exitosa:**  
    ```json
    {
      "message": "Restaurante creado exitosamente",
      "restaurant": {
        "id": 2,
        "name": "Mi Restaurante",
        "description": "Comida típica",
        "address": "Calle 123",
        "city": "Bogotá",
        "image_url": "http://..."
      }
    }
    ```

- **PUT /restaurants/<id>**  
  Actualiza un restaurante existente.
  - En el cuerpo JSON se pueden incluir los campos `name`, `description`, `address`, `city`, `image_url`.
  - **Respuesta exitosa:**  
    ```json
    {"message": "Restaurante actualizado"}
    ```

- **DELETE /restaurants/<id>**  
  Elimina un restaurante.
  - **Respuesta exitosa:**  
    ```json
    {"message": "Restaurante eliminado"}
    ```

### Reservas

- **POST /reservations**  
  Registra una nueva reserva.
  - Campos obligatorios: `restaurant_id`, `date` (YYYY-MM-DD), `table_number` (1 a 15).
  - **Cuerpo JSON de ejemplo:**
    ```json
    {
      "restaurant_id": 1,
      "date": "2024-07-21",
      "table_number": 5
    }
    ```
  - **Respuestas posibles:**
    - Reserva exitosa:
      ```json
      {"message": "Reserva creada", "reservation": { ... }}
      ```
    - Si se supera el cupo máximo del restaurante o global:
      ```json
      {"error": "No hay disponibilidad para la fecha seleccionada"}
      ```

- **GET /reservations**  
  Lista las reservas existentes.
  - Parámetros opcionales:  
    - `restaurant_id`, `date`, `table_number`
  - **Ejemplo de respuesta:**
    ```json
    [
      {
        "id": 1,
        "restaurant_id": 2,
        "date": "2024-07-21",
        "table_number": 5
      }
    ]
    ```

- **PUT /reservations/<id>**  
  Modifica una reserva. Permite cambiar `restaurant_id`, `date` y `table_number`.
  - **Respuesta exitosa:**  
    ```json
    {"message": "Reserva actualizada"}
    ```

- **DELETE /reservations/<id>**  
  Elimina una reserva.
  - **Respuesta exitosa:**  
    ```json
    {"message": "Reserva eliminada"}
    ```

---

## Pruebas

El proyecto incluye pruebas automatizadas con `pytest`.  
Para ejecutarlas:

```bash
pytest
```

---

## Notas adicionales

- Si realizas cambios en los modelos de datos, **recuerda correr las migraciones**.
- La API valida que **no se exceda el máximo de 15 reservas diarias por restaurante** y **20 reservas diarias en total**.
- Manejo de errores: Las respuestas de error siempre incluyen un campo `"error"` con la descripción.

---