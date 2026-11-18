# Software FJ — Fase 4, Programación UNAD (213023)

Proyecto académico individual del **Sistema Integral de Gestión de Clientes, Servicios y Reservas**. Desarrollado con Python 3.10 o superior y biblioteca estándar, **sin base de datos ni paquetes externos**.

## Ejecución

Abre la carpeta del proyecto en Visual Studio Code y ejecuta en la terminal:

```bash
python main.py
```

En Windows, si `python` no está disponible, prueba `py main.py`.

Para pruebas unitarias:

```bash
python -m unittest discover -s tests -v
```

## Estructura

- `modelos.py`: entidad abstracta, cliente encapsulado, servicio abstracto, sala, equipo, asesoría, reserva y excepciones.
- `gestor.py`: listas en memoria y reglas de negocio.
- `main.py`: 18 operaciones de demostración, captura de fallas y logging.
- `tests/test_sistema.py`: pruebas unitarias.
- `logs/eventos.log`: se genera automáticamente al ejecutar la demostración. No incluye información personal de clientes.

## Requisitos del anexo

- Abstracción: clases `Entidad` y `Servicio`.
- Herencia: `Cliente`, `Servicio` y `Reserva` extienden `Entidad`; `Sala`, `Equipo` y `Asesoria` extienden `Servicio`.
- Polimorfismo: `calcular_costo`, `validar_parametros` y `descripcion` en tres servicios.
- Encapsulación: propiedades con validación de `Cliente`.
- Sobrecarga: firmas `@overload` para `costo_final`; la implementación de Python usa parámetros opcionales.
- Excepciones: clases personalizadas, `try/except/else/finally`, y `raise ... from ...`.
- Registro de eventos: módulo `logging`.
- Persistencia: solo logs; clientes, servicios y reservas se conservan temporalmente en listas.

## Notas

Las tarifas y restricciones horarias son valores **simulados para demostrar las reglas del sistema**, no datos reales de Software FJ. La aplicación es una simulación de consola: no tiene interfaz gráfica ni almacenamiento permanente. Las fechas de prueba son ficticias.
