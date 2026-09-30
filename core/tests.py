from django.test import TestCase
from django.urls import reverse
from .models import Ingrediente, Producto, ProductoIngrediente, Usuario, Venta


class HeladeriaTests(TestCase):
    def setUp(self):
        self.cliente = Usuario.objects.create_user(
            "cliente", password="pass12345", rol=Usuario.Rol.CLIENTE
        )
        self.base = Ingrediente.objects.create(
            nombre="Vainilla", precio=2, calorias=100, inventario=5, tipo="BASE"
        )
        self.complemento = Ingrediente.objects.create(
            nombre="Nueces", precio=1, calorias=50, inventario=5, tipo="COMPLEMENTO"
        )
        self.extra = Ingrediente.objects.create(
            nombre="Crema", precio=1.5, calorias=30, inventario=5, tipo="COMPLEMENTO"
        )
        self.producto = Producto.objects.create(
            nombre="Copa", precio_publico=10, tipo="COPA", vaso="Alta"
        )
        ProductoIngrediente.objects.bulk_create(
            [
                ProductoIngrediente(producto=self.producto, ingrediente=i)
                for i in (self.base, self.complemento, self.extra)
            ]
        )

    def test_calculos_producto(self):
        self.assertEqual(self.producto.costo, 4.5)
        self.assertEqual(self.producto.calorias, 180)
        self.assertEqual(self.producto.rentabilidad, 5.5)

    def test_venta_descuenta_todos_los_ingredientes_y_registra(self):
        self.client.login(username="cliente", password="pass12345")
        response = self.client.post(
            reverse("vender_producto", args=[self.producto.pk]), {"cantidad": 2}
        )
        self.assertRedirects(
            response, reverse("producto_detalle", args=[self.producto.pk])
        )
        self.assertEqual(Venta.objects.get().total, 20)
        self.base.refresh_from_db()
        self.assertEqual(self.base.inventario, 3)

    def test_venta_no_permite_inventario_insuficiente(self):
        self.client.login(username="cliente", password="pass12345")
        self.client.post(
            reverse("vender_producto", args=[self.producto.pk]), {"cantidad": 6}
        )
        self.assertEqual(Venta.objects.count(), 0)
        self.base.refresh_from_db()
        self.assertEqual(self.base.inventario, 5)

    def test_complemento_se_renueva_a_cero(self):
        self.complemento.renovar_inventario(99)
        self.complemento.refresh_from_db()
        self.assertEqual(self.complemento.inventario, 0)

    def test_catalogo_es_publico(self):
        response = self.client.get(reverse("productos"))
        self.assertEqual(response.status_code, 200)
