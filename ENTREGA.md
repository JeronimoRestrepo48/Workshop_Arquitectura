# Tutorial 03 – DRF & API – Evidencia de entrega

## Requisitos de entrega (según tutorial)

1. **Archivo de log**: El sistema debe descontar inventario y generar el log de pagos (usando la Factory configurada en Taller 2). Mostrar que al comprar por API, la vista HTML de inventario/compra refleja el cambio (misma lógica de negocio para HTML y API).
2. **Captura de pantalla**: POST a `/api/v1/comprar/` con Postman o con la interfaz web de DRF.

Subir ambos a la asignación **"tutorial0-3 DRF&API"**.

---

## Cómo probar

### 1. Entorno

```bash
cd "Taller 3"
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
```

### 2. Datos de prueba

En `python manage.py shell`:

```python
from tienda_app.models import Libro, Inventario
l = Libro.objects.create(titulo="Arquitectura Limpia", precio=250.0)
Inventario.objects.create(libro=l, cantidad=5)
```

### 3. POST desde Postman

- **URL**: `http://127.0.0.1:8000/api/v1/comprar/`
- **Método**: POST
- **Body** (raw, JSON):

```json
{
  "libro_id": 1,
  "direccion_envio": "Calle 123"
}
```

Respuesta esperada (201): `{"estado":"exito","mensaje":"Orden creada. Total: ..."}`

### 4. Comprobar evidencia

- **Log de pagos**: Revisar el archivo `pagos_locales_JERONIMO_MORESTREPO_ANGEL.log` en la raíz del proyecto; debe aparecer una línea nueva por cada compra (por API o por vista HTML).
- **Inventario**: Comprar por API y luego abrir la vista HTML de compra del mismo libro (o admin de Inventario); el stock debe haber bajado.

### 5. Interfaz web de DRF

Con el servidor en marcha (`python manage.py runserver`), ir a:

`http://127.0.0.1:8000/api/v1/comprar/`

Ahí se puede hacer el POST desde el formulario HTML de DRF y usar esa pantalla para la captura de pantalla de la entrega.
