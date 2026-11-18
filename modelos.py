"""Entidades y servicios de Software FJ (UNAD, Programación 213023)."""
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import overload
import re
import uuid


class ErrorSistema(Exception):
    """Error controlado del dominio de la aplicación."""


class DatosInvalidos(ErrorSistema):
    """Se proporcionaron datos incompletos o inválidos."""


class ServicioNoDisponible(ErrorSistema):
    """El servicio no permite nuevas reservas."""


class ReservaInvalida(ErrorSistema):
    """La reserva no cumple las reglas del negocio."""


class OperacionNoPermitida(ErrorSistema):
    """Una transición o acción no está autorizada."""


def positivo(valor: object, campo: str) -> Decimal:
    """Valida y convierte un número positivo, evitando booleanos y NaN."""
    if isinstance(valor, bool) or valor is None:
        raise DatosInvalidos(f"{campo} debe ser numérico y positivo.")
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise DatosInvalidos(f"{campo} debe ser numérico.") from exc
    if not numero.is_finite() or numero <= 0:
        raise DatosInvalidos(f"{campo} debe ser mayor que cero y finito.")
    return numero


def porcentaje(valor: object, campo: str) -> Decimal:
    """Convierte un porcentaje entre 0 y 100."""
    if isinstance(valor, bool):
        raise DatosInvalidos(f"{campo} no puede ser booleano.")
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise DatosInvalidos(f"{campo} debe ser numérico.") from exc
    if not numero.is_finite() or not 0 <= numero <= 100:
        raise DatosInvalidos(f"{campo} debe estar entre 0 y 100.")
    return numero


class Entidad(ABC):
    """Abstracción básica de una entidad identificable."""

    def __init__(self, identificador: str | None = None) -> None:
        self._id = identificador or uuid.uuid4().hex[:8]

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def descripcion(self) -> str:
        """Entrega una descripción de la entidad."""


class Cliente(Entidad):
    """Cliente con nombre, correo y teléfono encapsulados."""

    def __init__(self, nombre: str, correo: str, telefono: str) -> None:
        super().__init__()
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise DatosInvalidos("El nombre debe tener al menos 3 caracteres.")
        self.__nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if not isinstance(valor, str) or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", valor.strip()):
            raise DatosInvalidos("El correo electrónico no es válido.")
        self.__correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        if not isinstance(valor, str) or not re.fullmatch(r"\+?\d{7,15}", valor.strip()):
            raise DatosInvalidos("El teléfono debe contener entre 7 y 15 dígitos.")
        self.__telefono = valor.strip()

    def descripcion(self) -> str:
        return f"Cliente {self.nombre} ({self.correo})"


class Servicio(Entidad, ABC):
    """Contrato abstracto para los servicios de Software FJ."""

    def __init__(self, nombre: str, tarifa_hora: object) -> None:
        super().__init__()
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatosInvalidos("El nombre del servicio es obligatorio.")
        self._nombre = nombre.strip()
        self._tarifa = positivo(tarifa_hora, "La tarifa")
        self._disponible = True

    @property
    def disponible(self) -> bool:
        return self._disponible

    def cambiar_disponibilidad(self, disponible: bool) -> None:
        if not isinstance(disponible, bool):
            raise DatosInvalidos("La disponibilidad debe ser booleana.")
        self._disponible = disponible

    @abstractmethod
    def validar_parametros(self, duracion: object) -> Decimal:
        """Comprueba requisitos del tipo de servicio."""

    @abstractmethod
    def calcular_costo(self, duracion: object) -> Decimal:
        """Calcula el precio base del servicio."""

    @abstractmethod
    def descripcion(self) -> str:
        """Describe el tipo específico de servicio."""

    @overload
    def costo_final(self, duracion: object) -> Decimal: ...

    @overload
    def costo_final(self, duracion: object, impuesto: object, descuento: object = 0) -> Decimal: ...

    def costo_final(self, duracion: object, impuesto: object = 0, descuento: object = 0) -> Decimal:
        """Variantes tipadas: precio base o precio con impuesto y descuento."""
        iva = porcentaje(impuesto, "El impuesto")
        rebaja = porcentaje(descuento, "El descuento")
        base = self.calcular_costo(duracion)
        return (base * (Decimal('1') - rebaja / 100) * (Decimal('1') + iva / 100)).quantize(Decimal('0.01'))


class Sala(Servicio):
    def __init__(self, nombre: str, tarifa_hora: object, capacidad: int) -> None:
        super().__init__(nombre, tarifa_hora)
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad < 1:
            raise DatosInvalidos("La capacidad de la sala debe ser un entero positivo.")
        self.capacidad = capacidad

    def validar_parametros(self, duracion: object) -> Decimal:
        horas = positivo(duracion, "La duración")
        if horas > 12:
            raise DatosInvalidos("La reserva de sala no puede superar 12 horas.")
        return horas

    def calcular_costo(self, duracion: object) -> Decimal:
        return self._tarifa * self.validar_parametros(duracion)

    def descripcion(self) -> str:
        return f"Sala {self._nombre}, capacidad {self.capacidad} personas"


class Equipo(Servicio):
    def __init__(self, nombre: str, tarifa_hora: object, referencia: str) -> None:
        super().__init__(nombre, tarifa_hora)
        if not isinstance(referencia, str) or not referencia.strip():
            raise DatosInvalidos("La referencia del equipo es obligatoria.")
        self.referencia = referencia.strip()

    def validar_parametros(self, duracion: object) -> Decimal:
        horas = positivo(duracion, "La duración")
        if horas > 72:
            raise DatosInvalidos("El alquiler de equipo no puede superar 72 horas.")
        return horas

    def calcular_costo(self, duracion: object) -> Decimal:
        return self._tarifa * self.validar_parametros(duracion)

    def descripcion(self) -> str:
        return f"Equipo {self._nombre}, referencia {self.referencia}"


class Asesoria(Servicio):
    def __init__(self, nombre: str, tarifa_hora: object, especialidad: str) -> None:
        super().__init__(nombre, tarifa_hora)
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise DatosInvalidos("La especialidad es obligatoria.")
        self.especialidad = especialidad.strip()

    def validar_parametros(self, duracion: object) -> Decimal:
        horas = positivo(duracion, "La duración")
        if horas > 8:
            raise DatosInvalidos("Una asesoría no puede superar 8 horas.")
        return horas

    def calcular_costo(self, duracion: object) -> Decimal:
        return self._tarifa * self.validar_parametros(duracion)

    def descripcion(self) -> str:
        return f"Asesoría {self._nombre}, especialidad {self.especialidad}"


class EstadoReserva(Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    PROCESADA = "procesada"
    CANCELADA = "cancelada"


class Reserva(Entidad):
    """Reserva con transiciones de estado controladas."""

    def __init__(self, cliente: Cliente, servicio: Servicio, duracion: object, inicio: datetime) -> None:
        super().__init__()
        if not isinstance(cliente, Cliente):
            raise DatosInvalidos("Se requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise DatosInvalidos("Se requiere un servicio válido.")
        if not isinstance(inicio, datetime):
            raise DatosInvalidos("La fecha de inicio no es válida.")
        if not servicio.disponible:
            raise ServicioNoDisponible("El servicio está fuera de servicio.")
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = servicio.validar_parametros(duracion)
        self.inicio = inicio
        self.estado = EstadoReserva.PENDIENTE
        self.total = servicio.costo_final(self.duracion)

    def confirmar(self) -> None:
        if self.estado != EstadoReserva.PENDIENTE:
            raise OperacionNoPermitida("Solo se pueden confirmar reservas pendientes.")
        if not self.servicio.disponible:
            raise ServicioNoDisponible("El servicio ya no está disponible.")
        self.estado = EstadoReserva.CONFIRMADA

    def procesar(self) -> None:
        if self.estado != EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitida("Solo se procesan reservas confirmadas.")
        self.estado = EstadoReserva.PROCESADA

    def cancelar(self) -> None:
        if self.estado not in (EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA):
            raise OperacionNoPermitida("No es posible cancelar una reserva procesada o cancelada.")
        self.estado = EstadoReserva.CANCELADA

    def descripcion(self) -> str:
        return f"Reserva {self.id} - {self.cliente.nombre} - {self.servicio.descripcion()} - {self.estado.value}"
