from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Ingrediente, Producto, ProductoIngrediente, Usuario


class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )


class IngredienteForm(forms.ModelForm):
    class Meta:
        model = Ingrediente
        fields = (
            "nombre",
            "precio",
            "calorias",
            "inventario",
            "es_vegetariano",
            "es_sano",
            "tipo",
            "sabor",
        )
        widgets = {"precio": forms.NumberInput(attrs={"step": "0.01"})}


class ProductoForm(forms.ModelForm):
    ingredientes = forms.ModelMultipleChoiceField(
        queryset=Ingrediente.objects.all(), widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Producto
        fields = (
            "nombre",
            "precio_publico",
            "tipo",
            "vaso",
            "volumen_onzas",
            "ingredientes",
        )

    def clean_ingredientes(self):
        ingredientes = self.cleaned_data["ingredientes"]
        if len(ingredientes) != 3:
            raise ValidationError(
                "Cada producto debe estar compuesto exactamente por 3 ingredientes."
            )
        return ingredientes

    def save(self, commit=True):
        producto = super().save(commit=commit)
        if commit:
            ProductoIngrediente.objects.filter(producto=producto).delete()
            ProductoIngrediente.objects.bulk_create(
                [
                    ProductoIngrediente(producto=producto, ingrediente=i)
                    for i in self.cleaned_data["ingredientes"]
                ]
            )
        return producto


class VentaForm(forms.Form):
    cantidad = forms.IntegerField(
        min_value=1, max_value=100, initial=1, label="Cantidad"
    )


class RenovarInventarioForm(forms.Form):
    cantidad = forms.IntegerField(min_value=0, required=False, label="Nueva cantidad")
