from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Ingrediente, Producto, ProductoIngrediente, Usuario, Venta


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Rol de negocio", {"fields": ("rol",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Rol de negocio", {"fields": ("rol",)}),)


admin.site.register(Ingrediente)
admin.site.register(Producto)
admin.site.register(ProductoIngrediente)
admin.site.register(Venta)
