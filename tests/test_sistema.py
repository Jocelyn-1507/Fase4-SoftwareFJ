"""Pruebas unitarias de las clases y las reglas de negocio."""
import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from modelos import (Cliente, Sala, Equipo, Asesoria, DatosInvalidos,
                     ReservaInvalida, OperacionNoPermitida, ServicioNoDisponible)
from gestor import Gestor


class PruebasSistema(unittest.TestCase):
    def setUp(self):
        self.gestor = Gestor()
        self.cliente = self.gestor.registrar_cliente('María Ruiz', 'maria@example.com', '3009876543')
        self.sala = self.gestor.registrar_servicio(Sala('Principal', 50000, 10))
        self.inicio = datetime(2030, 1, 10, 10)

    def test_cliente_valido(self):
        self.assertEqual(self.cliente.correo, 'maria@example.com')

    def test_correo_invalido(self):
        with self.assertRaises(DatosInvalidos):
            Cliente('María Ruiz', 'mal', '3009876543')

    def test_telefono_invalido(self):
        with self.assertRaises(DatosInvalidos):
            Cliente('María Ruiz', 'maria@example.com', '123')

    def test_duplicado(self):
        with self.assertRaises(DatosInvalidos):
            self.gestor.registrar_cliente('Otra Persona', 'MARIA@example.com', '3009876543')

    def test_tres_servicios_polimorficos(self):
        servicios = [self.sala, Equipo('Proyector', 20000, 'E1'), Asesoria('Python', 60000, 'TI')]
        self.assertEqual([s.calcular_costo(2) for s in servicios], [100000, 40000, 120000])

    def test_costo_impuesto_descuento(self):
        self.assertEqual(self.sala.costo_final(2, 19, 10), Decimal('107100.00'))

    def test_porcentajes_invalidos(self):
        with self.assertRaises(DatosInvalidos):
            self.sala.costo_final(2, 101, 0)

    def test_conflicto(self):
        self.gestor.crear_reserva(self.cliente, self.sala, 2, self.inicio)
        with self.assertRaises(ReservaInvalida):
            self.gestor.crear_reserva(self.cliente, self.sala, 1, self.inicio + timedelta(hours=1))

    def test_liberacion_por_cancelacion(self):
        r = self.gestor.crear_reserva(self.cliente, self.sala, 2, self.inicio)
        r.cancelar()
        segunda = self.gestor.crear_reserva(self.cliente, self.sala, 1, self.inicio)
        self.assertEqual(segunda.estado.value, 'pendiente')

    def test_transiciones(self):
        r = self.gestor.crear_reserva(self.cliente, self.sala, 2, self.inicio)
        r.confirmar()
        r.procesar()
        with self.assertRaises(OperacionNoPermitida):
            r.cancelar()

    def test_no_disponible(self):
        self.sala.cambiar_disponibilidad(False)
        with self.assertRaises(ServicioNoDisponible):
            self.gestor.crear_reserva(self.cliente, self.sala, 1, self.inicio)

    def test_duracion_negativa(self):
        with self.assertRaises(DatosInvalidos):
            self.gestor.crear_reserva(self.cliente, self.sala, -1, self.inicio)

    def test_no_inserta_reserva_fallida(self):
        with self.assertRaises(DatosInvalidos):
            self.gestor.crear_reserva(self.cliente, self.sala, -1, self.inicio)
        self.assertEqual(len(self.gestor.reservas), 0)

    def test_encadenamiento_de_excepciones(self):
        with self.assertRaises(DatosInvalidos) as cm:
            self.sala.calcular_costo('texto')
        self.assertIsNotNone(cm.exception.__cause__)


if __name__ == '__main__':
    unittest.main()
