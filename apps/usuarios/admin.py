from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioPersonalizado, Proveedor, Analitica, Trabajador

@admin.register(UsuarioPersonalizado)
class UsuarioPersonalizadoAdmin(UserAdmin):
    list_display = [
        'username', 'email', 'get_full_name', 'tipo_usuario', 
        'puesto', 'esta_activo', 'fecha_registro'
    ]
    list_filter = ['tipo_usuario', 'esta_activo', 'fecha_registro']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['fecha_registro']
    list_editable = ['esta_activo']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('tipo_usuario', 'telefono', 'puesto', 'fecha_registro', 'esta_activo')
        }),
    )
    
    def get_queryset(self, request):
        """Personalizar queryset según permisos"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser and request.user.tipo_usuario == 'jefe_proyectos':
            # Jefe de proyectos solo ve solicitantes
            return qs.filter(tipo_usuario='solicitante')
        return qs

@admin.register(Analitica)
class AnaliticaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'esta_activa', 'fecha_creacion']
    list_filter = ['esta_activa', 'fecha_creacion']
    search_fields = ['codigo', 'nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    list_editable = ['esta_activa']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion')
        }),
        ('Estado y Fechas', {
            'fields': ('esta_activa', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )
@admin.register(Trabajador)
class TrabajadorAdmin(admin.ModelAdmin):
    list_display = [
        'get_full_name', 'rfc', 'puesto', # <--- RFC en display
        'email', 'telefono', 'fecha_registro'
    ]
    list_filter = ['puesto', 'fecha_registro']
    search_fields = [
        'first_name', 'last_name', 'rfc', # <--- Búsqueda por RFC
        'puesto', 'email', 'telefono'
    ]
    readonly_fields = ['fecha_registro']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'puesto', 'email', 'telefono')
        }),
        ('Identificación', {
            'fields': ('rfc',) # <--- Solo RFC
        }),
        ('Fechas', {
            'fields': ('fecha_registro',)
        }),
    )

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = [
        'numero_proveedor', 'razon_social', 'rfc', 'ambito', 
        'tipo_proveedor', 'esta_activo', 'fecha_registro'
    ]
    list_filter = ['ambito', 'tipo_proveedor', 'esta_activo', 'fecha_registro']
    search_fields = ['numero_proveedor', 'razon_social', 'rfc', 'representante_legal']
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']
    list_editable = ['esta_activo']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_proveedor', 'razon_social', 'rfc', 'cedula_situacion_fiscal')
        }),
        ('Datos Fiscales y Contacto', {
            'fields': ('direccion_fiscal', 'representante_legal', 'curp_representante')
        }),
        ('Información Bancaria', {
            'fields': ('banco', 'numero_cuenta', 'clabe_interbancaria', 'swift_code')
        }),
        ('Contacto', {
            'fields': ('telefono_contacto', 'email_contacto', 'telefono_emergencia')
        }),
        ('Cartera de Servicios', {
            'fields': ('ambito', 'tipo_proveedor', 'cartera_servicios', 'terminos_pago')
        }),
        ('Estado y Fechas', {
            'fields': ('esta_activo', 'usuario', 'fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )