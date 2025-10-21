from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioPersonalizado, Proveedor

# Registrar el modelo de usuario personalizado
@admin.register(UsuarioPersonalizado)
class UsuarioPersonalizadoAdmin(UserAdmin):
    list_display = ['username', 'email', 'tipo_usuario', 'esta_activo', 'fecha_registro']
    list_filter = ['tipo_usuario', 'esta_activo']
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('tipo_usuario', 'telefono', 'puesto', 'esta_activo')}),
    )

# Registrar el modelo de proveedor
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['razon_social', 'rfc', 'usuario', 'telefono_contacto']
    search_fields = ['razon_social', 'rfc']