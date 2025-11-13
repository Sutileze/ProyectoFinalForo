from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError # Importar este error para manejar duplicidad
from django.contrib.auth.hashers import make_password, check_password
from .models import Comerciante # Importar la función para hashear
from .forms import RegistroComercianteForm, LoginForm
from django.utils import timezone

# Asumiendo que has definido RegistroComercianteForm y Comerciante en los archivos correspondientes
from .forms import RegistroComercianteForm 
# No necesitamos importar Comerciante directamente si solo usamos form.save()

def registro_comerciante_view(request):
    """
    Vista para manejar el registro de nuevos comerciantes.
    Maneja tanto la carga inicial de la página (GET) como el envío del formulario (POST).
    """
    if request.method == 'POST':
        # 1. Cuando el usuario envía el formulario (POST)
        form = RegistroComercianteForm(request.POST)
        if form.is_valid():
            
            # --- Lógica de Guardado ---
            # 2. Obtener y hashear la contraseña
            raw_password = form.cleaned_data.pop('password')
            hashed_password = make_password(raw_password)

            # 3. Crear el nuevo objeto Comerciante en memoria (sin guardar en DB aún)
            nuevo_comerciante = form.save(commit=False)
            
            # 4. Asignar el hash de la contraseña al campo del modelo
            nuevo_comerciante.password_hash = hashed_password
            
            # 5. La comuna ya se movió de 'comuna_select' a 'comuna' en forms.py
            # Solo verificamos que tenga un valor antes de guardar
            comuna_final = form.cleaned_data.get('comuna') 
            if comuna_final:
                nuevo_comerciante.comuna = comuna_final
            
            # 6. GUARDAR EL OBJETO COMPLETO EN LA BASE DE DATOS
            try:
                nuevo_comerciante.save()
                messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión.')
                # Redirección a la página de login
                return redirect('login') 
            
            # MANEJO ESPECÍFICO DEL ERROR DE EMAIL DUPLICADO (IntegrityError)
            except IntegrityError:
                # Si el email ya existe ( UNIQUE constraint en el campo email )
                messages.error(request, 'Este correo electrónico ya está registrado. Por favor, inicia sesión o usa otro correo.')
                print("ERROR DE DB: Intento de registro con email duplicado.")
            
            except Exception as e:
                # Esto atrapará cualquier otro error de DB o sistema
                messages.error(request, f'Ocurrió un error inesperado al guardar: {e}')
                print(f"ERROR DE DB GENERAL: {e}") 
                
        else:
            # Si la validación de forms.py falla (ej: contraseñas no coinciden, campos vacíos)
            messages.error(request, 'Por favor, corrige los errores del formulario.')
            
    else:
        # 7. Cuando la página se carga por primera vez (GET)
        form = RegistroComercianteForm()
    
    # Renderiza la plantilla, pasando el formulario (vacío en GET, con errores en POST fallido)
    context = {
        'form': form
    }
    return render(request, 'usuarios/cuenta.html', context)

# -------------------------------------------------------------------------------------
# VISTA DE LOGIN (PENDIENTE DE IMPLEMENTACIÓN)
# Necesaria para que el redirect('login') no cause un error de URL no encontrada
def login_view(request):
    """
    Vista para manejar el inicio de sesión de comerciantes registrados.
    Solo permite el acceso si el email existe en la base de datos y la contraseña es válida.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                # Buscar comerciante por email
                comerciante = Comerciante.objects.get(email=email)

                # Verificar contraseña
                if check_password(password, comerciante.password_hash):
                    # Actualizar última conexión
                    comerciante.ultima_conexion = timezone.now()
                    comerciante.save(update_fields=['ultima_conexion'])

                    messages.success(request, f'¡Bienvenido {comerciante.nombre_apellido}!')
                    return redirect('plataforma_comerciante')  # Asegúrate que esta URL esté definida

                else:
                    messages.error(request, 'Contraseña incorrecta. Intenta nuevamente.')

            except Comerciante.DoesNotExist:
                messages.error(request, 'Este correo no está registrado. Por favor, regístrate primero.')

        else:
            messages.error(request, 'Por favor, completa todos los campos correctamente.')

    else:
        form = LoginForm()

    context = {
        'form': form
    }
    return render(request, 'usuarios/cuenta.html', context)


def plataforma_comerciante_view(request):
    """
    Vista para la plataforma del comerciante.
    Actualmente es un placeholder que muestra un mensaje simple.
    """
    context = {
        'message': 'Bienvenido a la plataforma del comerciante. ¡Funcionalidad pendiente!'
    }
    return render(request, 'usuarios/plataforma_comerciante.html', context)