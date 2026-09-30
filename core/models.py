from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum


class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        EMPLEADO = "EMPLEADO", "Empleado"
        CLIENTE = "CLIENTE", "Cliente"

    rol = models.CharField(max_length=10, choices=Rol.choices, default=Rol.CLIENTE)

    def is_admin(self):
        return self.is_superuser or self.rol == self.Rol.ADMIN


class Ingrediente(models.Model):
    class Tipo(models.TextChoices):
        BASE = "BASE", "Base"
        COMPLEMENTO = "COMPLEMENTO", "Complemento"

    nombre = models.CharField(max_length=100, unique=True)
    precio = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    calorias = models.PositiveIntegerField(
        default=0, verbose_name="Calorías por porción"
    )
    inventario = models.PositiveIntegerField(default=0)
    es_vegetariano = models.BooleanField(default=True)
    es_sano = models.BooleanField(default=True)
    tipo = models.CharField(max_length=12, choices=Tipo.choices)
    sabor = models.CharField(
        max_length=80, blank=True, help_text="Principalmente para bases"
    )

    class Meta:
        ordering = ["tipo", "nombre"]
        verbose_name = "ingrediente"
        verbose_name_plural = "ingredientes"

    def __str__(self):
        return self.nombre

    def renovar_inventario(self, cantidad=None):
        self.inventario = 0 if self.tipo == self.Tipo.COMPLEMENTO else (cantidad or 0)
        self.save(update_fields=["inventario"])


class Producto(models.Model):
    class Tipo(models.TextChoices):
        COPA = "COPA", "Copa"
        MALTEADA = "MALTEADA", "Malteada"

    nombre = models.CharField(max_length=120, unique=True)
    precio_publico = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    vaso = models.CharField(max_length=80, blank=True, help_text="Requerido para copas")
    volumen_onzas = models.PositiveIntegerField(
        null=True, blank=True, help_text="Requerido para malteadas"
    )
    ingredientes = models.ManyToManyField(
        Ingrediente, through="ProductoIngrediente", related_name="productos"
    )

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    @property
    def costo(self):
        return self.ingredientes.aggregate(total=Sum("precio"))["total"] or Decimal(
            "0.00"
        )

    @property
    def calorias(self):
        return self.ingredientes.aggregate(total=Sum("calorias"))["total"] or 0

    @property
    def rentabilidad(self):
        return self.precio_publico - self.costo

    @property
    def margen_porcentaje(self):
        return (
            (self.rentabilidad / self.precio_publico * 100)
            if self.precio_publico
            else Decimal("0")
        )

    def clean(self):
        if self.tipo == self.Tipo.COPA and not self.vaso:
            raise ValidationError({"vaso": "Una copa debe indicar el tipo de vaso."})
        if self.tipo == self.Tipo.MALTEADA and not self.volumen_onzas:
            raise ValidationError(
                {"volumen_onzas": "Una malteada debe indicar su volumen."}
            )


class ProductoIngrediente(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["producto", "ingrediente"], name="producto_ingrediente_unico"
            )
        ]


class Venta(models.Model):
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name="ventas"
    )
    usuario = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, related_name="ventas"
    )
    cantidad = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"
