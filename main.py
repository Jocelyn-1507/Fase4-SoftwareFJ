"""Demostración reproducible de 17 operaciones válidas y fallidas."""
import logging
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal
from modelos import (Sala, Equipo, Asesoria, ErrorSistema,
                     ServicioNoDisponible)
from gestor import Gestor

LOG_FILE = Path(__file__).resolve().parent / "logs" / "eventos.log"
LOG_FILE.parent.mkdir(exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s",
                    encoding="utf-8")
logger = logging.getLogger("software_fj")


def ejecutar(numero: int, titulo: str, funcion, esperado: bool = True) -> bool:
    """Protege cada operación; la siguiente se ejecuta aunque esta falle."""
    print(f"\n[{numero:02}] {titulo}")
    try:
        resultado = funcion()
    except ErrorSistema as exc:
        logger.exception("Operación %02d fallida: %s", numero, titulo)
        print(f"  ERROR CONTROLADO: {exc}")
        return not esperado
    except Exception:
        logger.exception("Operación %02d: error no previsto", numero)
        print("  ERROR INESPERADO: consultar logs/eventos.log")
        return False
    else:
        logger.info("Operación %02d completada: %s", numero, titulo)
        print(f"  OK: {resultado if resultado is not None else 'completada'}")
        return esperado
    finally:
        # finally se ejecuta con éxito o error, sin cerrar la aplicación.
        print("  Finalizó la operación; el sistema continúa activo.")


def demostrar() -> bool:
    gestor = Gestor()
    datos = {}
    inicio = datetime(2030, 3, 10, 9, 0)
    resultados = []

    def guardar(clave, valor):
        datos[clave] = valor
        return getattr(valor, "descripcion", lambda: str(valor))()

    casos = [
        ("Registrar cliente válido", lambda: guardar('c1', gestor.registrar_cliente('Ana López', 'ana@example.com', '3001234567')), True),
        ("Rechazar correo inválido", lambda: gestor.registrar_cliente('Juan Pérez', 'correo-malo', '3001234567'), False),
        ("Registrar segundo cliente", lambda: guardar('c2', gestor.registrar_cliente('Luis Mora', 'luis@example.com', '3117654321')), True),
        ("Rechazar correo duplicado", lambda: gestor.registrar_cliente('Ana Dos', 'ANA@example.com', '3121234567'), False),
        ("Crear servicio de sala", lambda: guardar('sala', gestor.registrar_servicio(Sala('Sala Norte', 50000, 12))), True),
        ("Rechazar capacidad incorrecta", lambda: gestor.registrar_servicio(Sala('Sala Invalida', 30000, 0)), False),
        ("Crear servicio de equipo", lambda: guardar('equipo', gestor.registrar_servicio(Equipo('Proyector', 18000, 'EP-01'))), True),
        ("Crear servicio de asesoría", lambda: guardar('asesoria', gestor.registrar_servicio(Asesoria('Asesoría Python', 80000, 'Programación'))), True),
        ("Rechazar tarifa negativa", lambda: gestor.registrar_servicio(Equipo('Equipo malo', -1, 'ERR')), False),
        ("Crear reserva válida", lambda: guardar('r1', gestor.crear_reserva(datos['c1'], datos['sala'], 2, inicio)), True),
        ("Rechazar conflicto de horario", lambda: gestor.crear_reserva(datos['c2'], datos['sala'], 1, inicio + timedelta(hours=1)), False),
        ("Confirmar reserva", lambda: datos['r1'].confirmar(), True),
        ("Procesar reserva", lambda: datos['r1'].procesar(), True),
        ("Rechazar cancelación procesada", lambda: datos['r1'].cancelar(), False),
        ("Crear y cancelar segunda reserva", lambda: (lambda r: (r.cancelar(), r.descripcion()))(gestor.crear_reserva(datos['c2'], datos['equipo'], 3, inicio)), True),
        ("Rechazar servicio no disponible", lambda: (datos['asesoria'].cambiar_disponibilidad(False), gestor.crear_reserva(datos['c1'], datos['asesoria'], 1, inicio)), False),
        ("Calcular costo con IVA y descuento", lambda: f"$ {datos['sala'].costo_final(2, 19, 10):,.2f}", True),
        ("Rechazar duración inválida", lambda: gestor.crear_reserva(datos['c1'], datos['equipo'], -2, inicio + timedelta(days=1)), False),
    ]
    for numero, (titulo, operacion, esperado) in enumerate(casos, 1):
        resultados.append(ejecutar(numero, titulo, operacion, esperado))
    # Es una prueba automática de la propia demostración.
    print(f"\nRESULTADO: {sum(resultados)}/{len(resultados)} casos con respuesta esperada.")
    print(f"CLIENTES: {len(gestor.clientes)} | SERVICIOS: {len(gestor.servicios)} | RESERVAS: {len(gestor.reservas)}")
    print(f"Registro de eventos: {LOG_FILE}")
    return all(resultados)


if __name__ == '__main__':
    raise SystemExit(0 if demostrar() else 1)
