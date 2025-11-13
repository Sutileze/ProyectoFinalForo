from django.db import models

# Definición de opciones (CHOICES) para los campos de selección,
# tomadas directamente del HTML para asegurar la consistencia.

RELACION_NEGOCIO_CHOICES = [
    ('DUENO', 'Dueño/a'),
    ('CONYUGE', 'Cónyuge'),
    ('HIJO', 'Hijo/a'),
    ('TRABAJADOR', 'Trabajador/a'),
    ('OTRO_RELACION', 'Otro'),
]

TIPO_NEGOCIO_CHOICES = [
    ('ALMACEN', 'Almacén'),
    ('BOTILLERIA', 'Botillería'),
    ('CARNICERIA', 'Carnicería'),
    ('COMIDA_RAPIDA', 'Comida rápida'),
    ('FERIA_LIBRE', 'Feria libre'),
    ('FERRETERIA', 'Ferretería'),
    ('FRUTERIA', 'Frutería y Verdulería'),
    ('OTRO_NEGOCIO', 'Otro'),
]

class Comerciante(models.Model):
    """
    Modelo que representa a un comerciante registrado en la plataforma.
    Corresponde a la tabla 'comerciantes' en la base de datos.
    """
    # 1. Información Personal
    nombre_apellido = models.CharField(
        max_length=150,
        verbose_name='Nombre y Apellido completo'
    )
    email = models.EmailField(
        max_length=100,
        unique=True,
        verbose_name='Correo Electrónico (Único)'
    )
    whatsapp = models.CharField(
        max_length=20,
        verbose_name='Número de WhatsApp'
    )
    
    # 2. Seguridad
    password_hash = models.CharField(
        max_length=255,
        verbose_name='Hash de Contraseña'
    )

    # 3. Información del Negocio
    relacion_negocio = models.CharField(
        max_length=50,
        choices=RELACION_NEGOCIO_CHOICES,
        verbose_name='Relación con el Negocio'
    )

    tipo_negocio = models.CharField(
        max_length=50,
        choices=TIPO_NEGOCIO_CHOICES,
        verbose_name='Tipo de Negocio'
    )

    comuna = models.CharField(
        max_length=50,
        verbose_name='Comuna de Ubicación'
    )

    # 4. Metadatos de Registro
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro'
    )

    ultima_conexion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última Conexión'
    )

    class Meta:
        verbose_name = 'Comerciante'
        verbose_name_plural = 'Comerciantes'

    def __str__(self):
        # Representación legible del objeto Comerciante
        return f"{self.nombre_apellido} ({self.email})"