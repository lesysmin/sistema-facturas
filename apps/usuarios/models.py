from django.contrib.auth.models import AbstractUser
from django.db import models

class UsuarioPersonalizado(AbstractUser):
    TIPOS_USUARIO = [
        ('solicitante', 'Usuario Solicitante'),
        ('jefe_proyectos', 'Jefe de Proyectos'),
        ('jefe_compras', 'Jefa de Compras'),
        ('jefe_financiero', 'Jefe Financiero'),
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

class Proveedor(models.Model):
    usuario = models.OneToOneField(UsuarioPersonalizado, on_delete=models.CASCADE)
    rfc = models.CharField(max_length=13, unique=True)
    razon_social = models.CharField(max_length=255)
    direccion = models.TextField()
    numero_cuenta = models.CharField(max_length=20)
    telefono_contacto = models.CharField(max_length=15)
    email_contacto = models.EmailField()
    terminos_pago = models.IntegerField(default=30, help_text="Días para pago")
    
    def __str__(self):
        return self.razon_social