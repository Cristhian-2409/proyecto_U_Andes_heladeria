from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from .models import Usuario


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"/login/?next={request.path}")
            if request.user.is_superuser or request.user.rol in roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "No tienes permisos para realizar esta acción.")
            return redirect("productos")

        return wrapped

    return decorator


admin_or_employee_required = role_required(Usuario.Rol.ADMIN, Usuario.Rol.EMPLEADO)
admin_required = role_required(Usuario.Rol.ADMIN)
