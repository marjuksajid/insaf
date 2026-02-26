from django import forms

from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["name", "cellphone", "address"]
        widgets = {
            "name": forms.TextInput(attrs={"id": "name", "required": True}),
            "cellphone": forms.TextInput(attrs={"id": "cellphone", "required": True}),
            "address": forms.Textarea(attrs={"id": "address", "required": True, "rows": 3}),
        }
