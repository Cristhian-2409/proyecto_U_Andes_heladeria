from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from datetime import date
from .decorators import admin_or_employee_required
from .forms import (
    IngredienteForm,
    ProductoForm,
    RegistroForm,
    RenovarInventarioForm,
    VentaForm,
)
from .models import Ingrediente, Producto, Venta


def dashboard(request):
    productos = Producto.objects.all()[:6]
    contexto = {
        "productos": productos,
        "total_productos": Producto.objects.count(),
        "total_ingredientes": Ingrediente.objects.count(),
        "ventas_hoy": Venta.objects.filter(fecha__date=date.today()).aggregate(
            total=Sum("cantidad")
        )["total"]
        or 0,
    }
    return render(request, "dashboard.html", contexto)


def productos(request):
    lista = Producto.objects.prefetch_related("ingredientes").all()
    return render(request, "productos/lista.html", {"productos": lista})


def producto_detalle(request, pk):
    producto = get_object_or_404(
        Producto.objects.prefetch_related("ingredientes"), pk=pk
    )
    return render(
        request,
        "productos/detalle.html",
        {"producto": producto, "venta_form": VentaForm()},
    )


def producto_por_nombre(request, nombre):
    producto = get_object_or_404(
        Producto.objects.prefetch_related("ingredientes"), nombre__iexact=nombre
    )
    return render(
        request,
        "productos/detalle.html",
        {"producto": producto, "venta_form": VentaForm()},
    )


@login_required
def vender_producto(request, pk):
    if request.method != "POST":
        return redirect("producto_detalle", pk=pk)
    form = VentaForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Indica una cantidad válida.")
        return redirect("producto_detalle", pk=pk)
    cantidad = form.cleaned_data["cantidad"]
    with transaction.atomic():
        producto = (
            Producto.objects.select_for_update()
            .prefetch_related("ingredientes")
            .get(pk=pk)
        )
        ingredientes = list(
            Ingrediente.objects.select_for_update().filter(productos=producto)
        )
        if any(i.inventario < cantidad for i in ingredientes):
            agotados = ", ".join(
                i.nombre for i in ingredientes if i.inventario < cantidad
            )
            messages.error(request, f"Inventario insuficiente: {agotados}.")
            return redirect("producto_detalle", pk=pk)
        for ingrediente in ingredientes:
            ingrediente.inventario -= cantidad
            ingrediente.save(update_fields=["inventario"])
        Venta.objects.create(
            producto=producto,
            usuario=request.user,
            cantidad=cantidad,
            total=producto.precio_publico * cantidad,
        )
    messages.success(request, f"Venta registrada: {cantidad} × {producto.nombre}.")
    return redirect("producto_detalle", pk=pk)


@admin_or_employee_required
def producto_crear(request):
    form = ProductoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Producto creado correctamente.")
        return redirect("productos")
    return render(
        request, "productos/formulario.html", {"form": form, "titulo": "Nuevo producto"}
    )


@admin_or_employee_required
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, instance=producto)
    if request.method == "GET":
        form.initial["ingredientes"] = producto.ingredientes.all()
    if form.is_valid():
        form.save()
        messages.success(request, "Producto actualizado correctamente.")
        return redirect("producto_detalle", pk=pk)
    return render(
        request,
        "productos/formulario.html",
        {"form": form, "titulo": "Editar producto"},
    )


@admin_or_employee_required
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        producto.delete()
        messages.success(request, "Producto eliminado.")
    return redirect("productos")


def ingredientes(request):
    return render(
        request, "ingredientes/lista.html", {"ingredientes": Ingrediente.objects.all()}
    )


def ingrediente_detalle(request, pk):
    return render(
        request,
        "ingredientes/detalle.html",
        {"ingrediente": get_object_or_404(Ingrediente, pk=pk)},
    )


def ingrediente_por_nombre(request, nombre):
    return render(
        request,
        "ingredientes/detalle.html",
        {"ingrediente": get_object_or_404(Ingrediente, nombre__iexact=nombre)},
    )


@admin_or_employee_required
def ingrediente_crear(request):
    form = IngredienteForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Ingrediente creado correctamente.")
        return redirect("ingredientes")
    return render(
        request,
        "ingredientes/formulario.html",
        {"form": form, "titulo": "Nuevo ingrediente"},
    )


@admin_or_employee_required
def ingrediente_editar(request, pk):
    ingrediente = get_object_or_404(Ingrediente, pk=pk)
    form = IngredienteForm(request.POST or None, instance=ingrediente)
    if form.is_valid():
        form.save()
        messages.success(request, "Ingrediente actualizado.")
        return redirect("ingrediente_detalle", pk=pk)
    return render(
        request,
        "ingredientes/formulario.html",
        {"form": form, "titulo": "Editar ingrediente"},
    )


@admin_or_employee_required
def ingrediente_eliminar(request, pk):
    ingrediente = get_object_or_404(Ingrediente, pk=pk)
    if request.method == "POST":
        ingrediente.delete()
        messages.success(request, "Ingrediente eliminado.")
    return redirect("ingredientes")


@admin_or_employee_required
def renovar_inventario(request, pk):
    ingrediente = get_object_or_404(Ingrediente, pk=pk)
    form = RenovarInventarioForm(request.POST or None)
    if form.is_valid():
        ingrediente.renovar_inventario(form.cleaned_data["cantidad"])
        messages.success(request, f"Inventario de {ingrediente.nombre} renovado.")
        return redirect("ingrediente_detalle", pk=pk)
    return render(
        request, "ingredientes/renovar.html", {"form": form, "ingrediente": ingrediente}
    )


def registro(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegistroForm(request.POST or None)
    if form.is_valid():
        usuario = form.save()
        login(request, usuario)
        messages.success(request, "Cuenta creada. ¡Bienvenido!")
        return redirect("dashboard")
    return render(request, "registration/registro.html", {"form": form})
