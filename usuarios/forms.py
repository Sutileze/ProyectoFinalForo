from django import forms
from .models import Comerciante, RELACION_NEGOCIO_CHOICES, TIPO_NEGOCIO_CHOICES, Post, CATEGORIA_POST_CHOICES
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

# -------------------------------------------------------------------------------------
class PostForm(forms.ModelForm):
    # Campo personalizado para la URL/Link
    imagen_o_link = forms.URLField(
        required=False,
        label='URL de Imagen o Link',
        widget=forms.URLInput(attrs={
            'placeholder': 'Opcional: URL de una imagen o link relevante',
            'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-text-light dark:text-text-dark focus:outline-0 focus:ring-2 focus:ring-primary border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:border-primary h-12 placeholder:text-text-muted-light dark:placeholder:text-text-muted-dark p-[10px] text-base font-normal leading-normal'
        })
    )
    
    # Campo para etiquetas
    etiquetas_input = forms.CharField(
        required=False,
        label='Etiquetas',
        help_text='Etiqueta a otros usuarios o agrega hashtags, separados por coma (ej: @JuanPerez, #Marketing)',
        widget=forms.TextInput(attrs={
            'placeholder': '@usuario, #hashtag',
            'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-text-light dark:text-text-dark focus:outline-0 focus:ring-2 focus:ring-primary border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:border-primary h-12 placeholder:text-text-muted-light dark:placeholder:text-text-muted-dark p-[10px] text-base font-normal leading-normal'
        })
    )

    class Meta:
        model = Post
        fields = ('titulo', 'contenido', 'categoria') # Usaremos los campos personalizados en clean()
        
        widgets = {
            'titulo': forms.TextInput(attrs={
                'placeholder': 'Un título claro y conciso',
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-text-light dark:text-text-dark focus:outline-0 focus:ring-2 focus:ring-primary border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:border-primary h-12 placeholder:text-text-muted-light dark:placeholder:text-text-muted-dark p-[10px] text-base font-normal leading-normal'
            }),
            'contenido': forms.Textarea(attrs={
                'placeholder': 'Escribe aquí el contenido de tu publicación...',
                'rows': 5,
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-text-light dark:text-text-dark focus:outline-0 focus:ring-2 focus:ring-primary border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:border-primary placeholder:text-text-muted-light dark:placeholder:text-text-muted-dark p-[10px] text-base font-normal leading-normal'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select flex w-full min-w-0 flex-1 rounded-lg text-text-light dark:text-text-dark focus:outline-0 focus:ring-2 focus:ring-primary border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:border-primary h-12 placeholder:text-text-muted-light dark:placeholder:text-text-muted-dark p-[10px] text-base font-normal leading-normal'
            }, choices=CATEGORIA_POST_CHOICES),
        }

    # Asigna los campos personalizados a los campos del modelo antes de guardar
    def clean(self):
        cleaned_data = super().clean()
        
        # Obtenemos los campos personalizados usando .pop() para eliminarlos de cleaned_data
        imagen_o_link = self.cleaned_data.pop('imagen_o_link', None)
        etiquetas_input = self.cleaned_data.pop('etiquetas_input', None)

        if imagen_o_link:
            cleaned_data['imagen_url'] = imagen_o_link
        
        if etiquetas_input:
            cleaned_data['etiquetas'] = etiquetas_input

        return cleaned_data

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password, check_password
from .models import Comerciante, Post # <-- Importar Post
from .forms import RegistroComercianteForm, LoginForm, PostForm # <-- Importar PostForm
from django.utils import timezone

# ... (registro_comerciante_view y login_view se mantienen) ...

# NUEVA VISTA PARA CREAR PUBLICACIONES (solo procesa el POST)
def crear_publicacion_view(request):
    # En una aplicación real, usarías @login_required y request.user.comerciante
    if request.method == 'POST':
        try:
            # Placeholder: Obtener el primer comerciante disponible (simulación de usuario logueado)
            comerciante_simulado = Comerciante.objects.first() 
            if not comerciante_simulado:
                messages.error(request, 'Error: No hay usuarios registrados.')
                return redirect('registro') 
            
            form = PostForm(request.POST)
            if form.is_valid():
                nuevo_post = form.save(commit=False)
                nuevo_post.comerciante = comerciante_simulado # Asigna el comerciante
                
                # Los campos adicionales (imagen_url y etiquetas) ya se prepararon en form.clean()
                
                nuevo_post.save()
                messages.success(request, '¡Publicación creada con éxito! Se ha añadido al foro.')
                return redirect('plataforma_comerciante')
            else:
                # Si la validación falla (ej. campos requeridos vacíos)
                messages.error(request, 'Por favor, corrige los errores en el formulario de publicación.')
                # Se redirige con el error, pero el formulario se perderá.
                return redirect('plataforma_comerciante') # Redirigir a la plataforma
        
        except Exception as e:
            messages.error(request, f'Ocurrió un error al publicar: {e}')
            print(f"ERROR AL CREAR POST: {e}")
            
    # Si se accede por GET, simplemente redirige a la plataforma
    return redirect('plataforma_comerciante')


# VISTA PRINCIPAL DE LA PLATAFORMA DE COMERCIANTE (Modificada)
def plataforma_comerciante_view(request):
    """
    Vista para la plataforma del comerciante, que ahora maneja el filtro de foro.
    """
    
    # 1. Manejo del Filtro de Categoría
    categoria_filtro = request.GET.get('categoria', None)
    
    if categoria_filtro and categoria_filtro != 'TODAS':
        # Filtra por la clave corta (ej: 'DUDA')
        posts = Post.objects.filter(categoria=categoria_filtro)
    else:
        posts = Post.objects.all() # Todos los posts por defecto
        categoria_filtro = 'TODAS'
        
    # 2. Obtener el formulario de publicación vacío para el modal
    post_form = PostForm()

    # 3. Datos de Contexto
    context = {
        'post_form': post_form,
        'posts': posts,
        'CATEGORIA_POST_CHOICES': Post.CATEGORIA_POST_CHOICES,
        'categoria_seleccionada': categoria_filtro,
        'message': 'Bienvenido a la plataforma del comerciante.'
    }
    
    return render(request, 'usuarios/plataforma_comerciante.html', context)