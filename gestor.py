"""Gestor en memoria, validación de duplicados y conflictos horarios."""
from datetime import datetime, timedelta
import logging
from modelos import (Cliente, Servicio, Reserva, DatosInvalidos, ReservaInvalida,
                     EstadoReserva)

logger = logging.getLogger("software_fj")


class Gestor:
    def __init__(self) -> None:
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []

    def registrar_cliente(self, nombre: str, correo: str, telefono: str) -> Cliente:
        # La validación se realiza antes de agregar el objeto a la lista.
        cliente = Cliente(nombre, correo, telefono)
        if any(c.correo == cliente.correo for c in self.clientes):
            raise DatosInvalidos("El correo ya se encuentra registrado.")
        self.clientes.append(cliente)
        logger.info("Cliente registrado: id=%s", cliente.id)
        return cliente

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        if not isinstance(servicio, Servicio):
            raise DatosInvalidos("Se debe proporcionar un servicio válido.")
        self.servicios.append(servicio)
        logger.info("Servicio registrado: %s", servicio.descripcion())
        return servicio

    def crear_reserva(self, cliente: Cliente, servicio: Servicio, duracion: object,
                      inicio: datetime) -> Reserva:
        if cliente not in self.clientes or servicio not in self.servicios:
            raise ReservaInvalida("Cliente o servicio no registrado en el sistema.")
        # La entidad valida sus parámetros antes de insertarse en memoria.
        nueva = Reserva(cliente, servicio, duracion, inicio)
        fin = inicio + timedelta(hours=float(nueva.duracion))
        for existente in self.reservas:
            if existente.servicio is not servicio or existente.estado == EstadoReserva.CANCELADA:
                continue
            fin_existente = existente.inicio + timedelta(hours=float(existente.duracion))
            if inicio < fin_existente and existente.inicio < fin:
                raise ReservaInvalida("Existe una reserva que se superpone para este servicio.")
        self.reservas.append(nueva)
        logger.info("Reserva creada: id=%s", nueva.id)
        return nueva
