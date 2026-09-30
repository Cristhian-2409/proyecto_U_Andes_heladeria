from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("productos/", views.productos, name="productos"),
    path(
        "productos/nombre/<str:nombre>/",
        views.producto_por_nombre,
        name="producto_nombre",
    ),
    path("productos/<int:pk>/", views.producto_detalle, name="producto_detalle"),
    path("productos/<int:pk>/vender/", views.vender_producto, name="vender_producto"),
    path("productos/nuevo/", views.producto_crear, name="producto_crear"),
    path("productos/<int:pk>/editar/", views.producto_editar, name="producto_editar"),
    path(
        "productos/<int:pk>/eliminar/",
        views.producto_eliminar,
        name="producto_eliminar",
    ),
    path("ingredientes/", views.ingredientes, name="ingredientes"),
    path(
        "ingredientes/nombre/<str:nombre>/",
        views.ingrediente_por_nombre,
        name="ingrediente_nombre",
    ),
    path(
        "ingredientes/<int:pk>/", views.ingrediente_detalle, name="ingrediente_detalle"
    ),
    path(
        "ingredientes/<int:pk>/renovar/",
        views.renovar_inventario,
        name="renovar_inventario",
    ),
    path("ingredientes/nuevo/", views.ingrediente_crear, name="ingrediente_crear"),
    path(
        "ingredientes/<int:pk>/editar/",
        views.ingrediente_editar,
        name="ingrediente_editar",
    ),
    path(
        "ingredientes/<int:pk>/eliminar/",
        views.ingrediente_eliminar,
        name="ingrediente_eliminar",
    ),
    path("registro/", views.registro, name="registro"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
