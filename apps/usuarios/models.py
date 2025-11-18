from django.contrib.auth.models import AbstractUser
from django.db import models

class UsuarioPersonalizado(AbstractUser):
    TIPOS_USUARIO = [
        ('solicitante', 'Usuario Solicitante'),
        ('jefe_proyectos', 'Jefe de Proyectos'),
        ('jefe_compras', 'Jefe de Compras'),
        ('jefe_financiero', 'Jefe Financiero'),
        ('rh', 'Recursos Humanos'),  # NUEVO ROL AGREGADO
        ('proveedor', 'Proveedor'),
        ('admin_general', 'Administrador General'),
    ]
    
    tipo_usuario = models.CharField(max_length=20, choices=TIPOS_USUARIO, default='solicitante')
    telefono = models.CharField(max_length=15, blank=True)
    puesto = models.CharField(max_length=100, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    esta_activo = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.get_tipo_usuario_display()}"
    
    def es_jefe_proyectos(self):
        return self.tipo_usuario == 'jefe_proyectos'
    
    def es_solicitante(self):
        return self.tipo_usuario == 'solicitante'
    
    def es_proveedor(self):
        return self.tipo_usuario == 'proveedor'
    
    def es_jefe_compras(self):
        return self.tipo_usuario == 'jefe_compras'
    
    def es_rh(self):
        return self.tipo_usuario == 'rh'  # NUEVO MÉTODO
    
    def puede_registrar_usuarios(self):
        """Define qué roles pueden registrar usuarios"""
        return self.tipo_usuario in ['jefe_proyectos', 'admin_general']  # RH ELIMINADO
    
    def puede_gestionar_analiticas(self):
        """Define qué roles pueden gestionar analíticas"""
        return self.tipo_usuario in ['rh', 'admin_general']  # NUEVO MÉTODO


class Analitica(models.Model):
    """Modelo para gestionar códigos de proyectos específicos (analíticas)"""
    codigo = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name="Código de Analítica",
        help_text="Código único del proyecto (ej: MX1234567)"
    )
    nombre = models.CharField(
        max_length=255,
        verbose_name="Nombre del Proyecto",
        help_text="Nombre descriptivo del proyecto (ej: Mantenimiento Río Verde)"
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción detallada del proyecto"
    )
    esta_activa = models.BooleanField(default=True, verbose_name="Activa")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Analítica"
        verbose_name_plural = "Analíticas"
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Trabajador(models.Model):
    """Modelo para representar a un empleado/trabajador que NO necesariamente tiene acceso al sistema."""
    
    first_name = models.CharField(max_length=150, verbose_name="Nombre(s)")
    last_name = models.CharField(max_length=150, verbose_name="Apellido(s)")
    
    # NUEVO CAMPO DE IDENTIFICACIÓN: RFC
    rfc = models.CharField(
        max_length=13, 
        unique=True,
        verbose_name="RFC (Registro Federal de Contribuyentes)",
        help_text="Clave única de identificación fiscal."
    )
    
    puesto = models.CharField(max_length=100, verbose_name="Puesto o Cargo")
    email = models.EmailField(
        max_length=254, 
        blank=True, 
        null=True, 
        verbose_name="Email de Contacto"
    )
    telefono = models.CharField(max_length=15, blank=True, verbose_name="Teléfono")
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    esta_activo = models.BooleanField(default=True, verbose_name="Activo")
    class Meta:
        verbose_name = "Trabajador (Recurso)"
        verbose_name_plural = "Trabajadores (Recursos)"
        ordering = ['last_name', 'first_name']
        
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.rfc})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class Proveedor(models.Model):
    AMBITO_CHOICES = [
        ('local', 'Local'),
        ('nacional', 'Nacional'),
        ('internacional', 'Internacional'),
    ]
    
    TIPO_PROVEEDOR_CHOICES = [
        ('bienes', 'Proveedor de Bienes'),
        ('servicios', 'Proveedor de Servicios'),
        ('ambos', 'Proveedor de Bienes y Servicios'),
    ]
    
    # Información básica
    numero_proveedor = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name="Número de Proveedor",
        help_text="Número único identificador del proveedor",
        default="PROV-TEMP"
    )
    
    # Datos fiscales
    rfc = models.CharField(
        max_length=13, 
        unique=True,
        verbose_name="RFC",
        help_text="Registro Federal de Contribuyentes",
        default="XAXX010101000"
    )
    
    cedula_situacion_fiscal = models.CharField(
        max_length=50,
        verbose_name="Cédula de Situación Fiscal",
        help_text="Constancia de situación fiscal",
        default="Por definir"
    )
    
    razon_social = models.CharField(
        max_length=255, 
        verbose_name="Razón Social",
        default="Por definir"
    )
    direccion_fiscal = models.TextField(
        verbose_name="Dirección Fiscal",
        default="Dirección por definir"
    )
    
    # Datos bancarios
    banco = models.CharField(
        max_length=100, 
        help_text="Nombre del banco",
        default="Banco por definir"
    )
    numero_cuenta = models.CharField(
        max_length=20, 
        verbose_name="Número de Cuenta",
        default="Por definir"
    )
    clabe_interbancaria = models.CharField(
        max_length=18,
        blank=True,
        verbose_name="CLABE Interbancaria",
        help_text="18 dígitos",
        default=""
    )
    swift_code = models.CharField(
        max_length=11,
        blank=True,
        verbose_name="Código SWIFT",
        help_text="Para transferencias internacionales",
        default=""
    )
    
    # Representante legal
    representante_legal = models.CharField(
        max_length=255, 
        verbose_name="Representante Legal",
        default="Por definir"
    )
    curp_representante = models.CharField(
        max_length=18,
        blank=True,
        verbose_name="CURP del Representante",
        default=""
    )
    
    # Contacto
    telefono_contacto = models.CharField(
        max_length=15, 
        verbose_name="Teléfono de Contacto",
        default="Por definir"
    )
    email_contacto = models.EmailField(
        verbose_name="Email de Contacto",
        default="contacto@proveedor.com"
    )
    telefono_emergencia = models.CharField(
        max_length=15, 
        blank=True,
        verbose_name="Teléfono de Emergencia",
        default=""
    )
    
    # Cartera que ofrecen
    ambito = models.CharField(
        max_length=20,
        choices=AMBITO_CHOICES,
        default='nacional',
        verbose_name="Ámbito de Operación"
    )
    
    tipo_proveedor = models.CharField(
        max_length=20,
        choices=TIPO_PROVEEDOR_CHOICES,
        default='bienes',
        verbose_name="Tipo de Proveedor"
    )
    
    cartera_servicios = models.TextField(
        blank=True,
        verbose_name="Cartera de Servicios/Productos",
        help_text="Descripción detallada de los servicios o productos que ofrece",
        default="Servicios por definir"
    )
    
    # Términos y condiciones
    terminos_pago = models.IntegerField(
        default=30, 
        verbose_name="Términos de Pago",
        help_text="Días para pago"
    )
    
    # Estados
    esta_activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Relación con usuario (opcional, para acceso al sistema)
    usuario = models.OneToOneField(
        UsuarioPersonalizado, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proveedor_perfil'
    )
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['razon_social']
    
    def __str__(self):
        return f"{self.numero_proveedor} - {self.razon_social}"
    
    @property
    def informacion_contacto(self):
        return f"{self.telefono_contacto} | {self.email_contacto}"
    
    @property
    def informacion_bancaria(self):
        return f"{self.banco} - {self.numero_cuenta}"