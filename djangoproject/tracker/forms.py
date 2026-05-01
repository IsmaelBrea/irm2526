from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded text-slate-50 focus:outline-none focus:border-green-500",
                "placeholder": "Correo electrónico",
            }
        ),
    )
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded text-slate-50 focus:outline-none focus:border-green-500",
                "placeholder": "Nombre de usuario",
            }
        ),
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded text-slate-50 focus:outline-none focus:border-green-500",
                "placeholder": "Contraseña",
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded text-slate-50 focus:outline-none focus:border-green-500",
                "placeholder": "Confirmar contraseña",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class UserLoginForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded text-slate-50 focus:outline-none focus:border-green-500",
                "placeholder": "Usuario o correo",
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded text-slate-50 focus:outline-none focus:border-green-500",
                "placeholder": "Contraseña",
            }
        )
    )
