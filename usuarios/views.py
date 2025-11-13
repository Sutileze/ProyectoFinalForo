from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError 
from django.contrib.auth.hashers import make_password, check_password
# Importación Corregida: Importa CATEGORIA_POST_CHOICES junto a Comerciante y Post
from .models import Comerciante, Post, CATEGORIA_POST_CHOICES 
from .forms import RegistroComercianteForm, LoginForm, PostForm 
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
# VISTA DE LOGIN
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

# -------------------------------------------------------------------------------------
# VISTA PARA CREAR PUBLICACIONES (NUEVA FUNCIÓN)
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
        # MODIFICACIÓN CLAVE: Usar la variable importada directamente, no a través de Post
        'CATEGORIA_POST_CHOICES': CATEGORIA_POST_CHOICES, 
        'categoria_seleccionada': categoria_filtro,
        'message': 'Bienvenido a la plataforma del comerciante.'
    }
    
    return render(request, 'usuarios/plataforma_comerciante.html', context)