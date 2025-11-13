from django import forms
from .models import Comerciante, RELACION_NEGOCIO_CHOICES, TIPO_NEGOCIO_CHOICES

# Opciones de comuna
COMUNA_CHOICES = [
    ('', 'Selecciona tu comuna'),
    ('ARICA', 'Arica'),
    ('SANTIAGO', 'Santiago'),
    ('PROVIDENCIA', 'Providencia'),
    ('LA_SERENA', 'La Serena'),
    ('VALPARAISO', 'Valparaíso'),
    ('OTRO_COMUNA', '...'),
]

class RegistroComercianteForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Mínimo 8 caracteres', 'id': 'password'}),
        max_length=255
    )
    confirm_password = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repite la contraseña', 'id': 'confirm-password'}),
        max_length=255
    )
    comuna_select = forms.ChoiceField(
        choices=COMUNA_CHOICES,
        label='Comuna',
        widget=forms.Select(attrs={'id': 'commune'})
    )

    class Meta:
        model = Comerciante
        fields = (
            'nombre_apellido', 'email', 'whatsapp',
            'relacion_negocio', 'tipo_negocio',
        )
        widgets = {
            'nombre_apellido': forms.TextInput(attrs={'placeholder': 'Ej: Juan Pérez', 'id': 'fullname'}),
            'email': forms.EmailInput(attrs={'placeholder': 'tucorreo@ejemplo.com', 'id': 'email'}),
            'whatsapp': forms.TextInput(attrs={'placeholder': '+56 9 1234 5678', 'id': 'whatsapp'}),
            'relacion_negocio': forms.Select(attrs={'id': 'business-relation'}),
            'tipo_negocio': forms.Select(attrs={'id': 'business-type'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Las contraseñas no coinciden.')

        if password and len(password) < 8:
            self.add_error('password', 'La contraseña debe tener al menos 8 caracteres.')

        comuna = cleaned_data.get('comuna_select')
        cleaned_data['comuna'] = comuna

        return cleaned_data

# ✅ Formulario de Login separado
class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu correo'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña'
        })
    )
