from django.core.management.base import BaseCommand
from core.models import Ingrediente, Producto, ProductoIngrediente, Usuario


class Command(BaseCommand):
    help = "Crea usuarios y catálogo de demostración."

    def handle(self, *args, **options):
        admin, created = Usuario.objects.get_or_create(
            username="admin",
            defaults={
                "rol": Usuario.Rol.ADMIN,
                "email": "admin@dulcenube.local",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("Admin123!")
            admin.save()
        empleado, created = Usuario.objects.get_or_create(
            username="empleado", defaults={"rol": Usuario.Rol.EMPLEADO}
        )
        if created:
            empleado.set_password("Empleado123!")
            empleado.save()
        ingredientes = [
            ("Vainilla", "BASE", 1800, 210, 30, "Vainilla"),
            ("Chocolate", "BASE", 2200, 240, 30, "Chocolate"),
            ("Fresa", "BASE", 2000, 160, 25, "Fresa"),
            ("Chispas de chocolate", "COMPLEMENTO", 800, 70, 20, ""),
            ("Nueces", "COMPLEMENTO", 1200, 90, 15, ""),
            ("Crema batida", "COMPLEMENTO", 900, 50, 20, ""),
        ]
        objects = []
        for nombre, tipo, precio, calorias, inventario, sabor in ingredientes:
            obj, _ = Ingrediente.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "tipo": tipo,
                    "precio": precio,
                    "calorias": calorias,
                    "inventario": inventario,
                    "sabor": sabor,
                    "es_sano": nombre in ("Fresa", "Nueces"),
                },
            )
            objects.append(obj)
        for nombre, tipo, precio, selected in [
            ("Copa Arcoíris", "COPA", 10500, [0, 2, 3]),
            ("Malteada Crunch", "MALTEADA", 13500, [1, 4, 5]),
        ]:
            producto, _ = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "tipo": tipo,
                    "precio_publico": precio,
                    "vaso": "Copa alta" if tipo == "COPA" else "",
                    "volumen_onzas": None if tipo == "COPA" else 16,
                },
            )
            for index in selected:
                ProductoIngrediente.objects.get_or_create(
                    producto=producto, ingrediente=objects[index]
                )
        self.stdout.write(
            self.style.SUCCESS("Datos demo creados. Admin: admin / Admin123!")
        )
