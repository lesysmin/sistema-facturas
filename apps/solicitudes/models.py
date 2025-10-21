from django.db import models
from django.core.validators import RegexValidator
from usuarios.models import UsuarioPersonalizado

# Validador para la analitica (MX seguido de 7 numeros)
validar_analitica = RegexValidator(
    regex=r'^MX\d{7}$',
    message='La analitica debe tener el formato MX seguido de 7 numeros. Ejemplo: MX1234567',
    code='analitica_invalida'
)

class SolicitudCompra(models.Model):
    ESTADOS_SC = [
        ('pendiente', 'Pendiente de Validacion'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('cotizacion', 'En Cotizacion'),
        ('completada', 'Completada'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    ]
    
    CODIFICACION_CHOICES = [
        ('A', 'A - EPP. Equipo de protección personal'),
        ('B', 'B - Equipos LOTO'),
        ('C', 'C - FORMACIONES'),
        ('D', 'D - UNIFORMES'),
        ('E', 'E - GESTIÓN DE PROYECTOS'),
        ('F', 'F - VEHÍCULOS'),
        ('G', 'G - GASTOS MÉDICOS EVENTUALES'),
        ('H', 'H - GASTOS COVID'),
        ('I', 'I - HERRAMIENTA MENOR'),
        ('J', 'J - EQUIPO DE MANIOBRA EN MT Y AT'),
        ('K', 'K - CONSUMIBLES'),
        ('L', 'L - SERVICIOS'),
        ('M', 'M - HERRAMIENTA CALIBRADA Y CALIBRACIONES'),
        ('N', 'N - HERRAMIENTA ESPECIALIZADA'),
        ('O', 'O - ÚTILES DE IZAJE Y MANIOBRA'),
    ]
    
    numero_sc = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Numero de SC",
        help_text="Ingrese un número único para la solicitud. Ejemplo: SC-2024-001"
    )
    
    prioridad = models.CharField(
        max_length=10,
        choices=PRIORIDAD_CHOICES,
        default='media',
        verbose_name="Prioridad"
    )
    
    codificacion = models.CharField(
        max_length=1,
        choices=CODIFICACION_CHOICES,
        default='K',  # VALOR POR DEFECTO AGREGADO
        verbose_name="Codificación de Compra",
        help_text="Seleccione la categoría de la compra"
    )
    
    solicitante = models.ForeignKey(UsuarioPersonalizado, on_delete=models.CASCADE, related_name='solicitudes_creadas')
    
    # Analitica con formato MX + 7 numeros (puede repetirse)
    analitica = models.CharField(
        max_length=9, 
        validators=[validar_analitica],
        help_text="Formato: MX seguido de 7 numeros. Ejemplo: MX1234567"
    )
    
    descripcion = models.TextField(verbose_name="Descripcion", help_text="Descripcion detallada de lo que se necesita")
    
    presupuesto_maximo = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Presupuesto Maximo Aprobado"
    )
    
    archivo_pdf = models.FileField(
        upload_to='solicitudes/pdf/', 
        verbose_name="Archivo PDF",
        help_text="Adjuntar documento PDF de la solicitud"
    )
    
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS_SC, 
        default='pendiente'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creacion")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualizacion")
    comentario_rechazo = models.TextField(blank=True, verbose_name="Comentario de Rechazo")
    
    class Meta:
        verbose_name = "Solicitud de Compra"
        verbose_name_plural = "Solicitudes de Compra"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.numero_sc} - {self.solicitante.get_full_name()}"
    
    @property
    def total_items(self):
        """Calcular el total sumando todos los items"""
        return sum(item.precio_total for item in self.items.all())
    
    @property
    def cantidad_items(self):
        """Obtener la cantidad de items en la solicitud"""
        return self.items.count()

    def get_codificacion_display_full(self):
        """Obtener la descripción completa de la codificación"""
        return dict(self.CODIFICACION_CHOICES).get(self.codificacion, '')


class ItemSolicitud(models.Model):
    solicitud = models.ForeignKey(SolicitudCompra, on_delete=models.CASCADE, related_name='items')
    
    descripcion = models.CharField(
        max_length=200, 
        verbose_name="Descripcion del Item",
        help_text="Descripcion detallada del producto o servicio"
    )
    
    cantidad = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Cantidad",
        help_text="Cantidad requerida"
    )
    
    precio_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Precio Unitario",
        help_text="Precio por unidad"
    )
    
    precio_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name="Precio Total",
        editable=False  # Se calcula automaticamente
    )
    
    class Meta:
        verbose_name = "Item de Solicitud"
        verbose_name_plural = "Items de Solicitud"
    
    def save(self, *args, **kwargs):
        # Calcular automaticamente el precio total
        self.precio_total = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.descripcion} - {self.cantidad} x ${self.precio_unitario}"