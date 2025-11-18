from django.contrib import admin
from .models import SolicitudCompra


@admin.register(SolicitudCompra)
class SolicitudCompraAdmin(admin.ModelAdmin):
    list_display = [
        'numero_sc', 
        'solicitante', 
        'prioridad',
        'codificacion',
        'analitica', 
        'estado', 
        'fecha_creacion'
    ]
    list_filter = ['estado', 'prioridad', 'codificacion', 'fecha_creacion']
    search_fields = ['numero_sc', 'analitica', 'solicitante__username', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero_sc', 'solicitante', 'prioridad', 'codificacion')
        }),
        ('Detalles de la Solicitud', {
            'fields': ('analitica', 'descripcion', 'archivo_pdf')
        }),
        ('Presupuesto y Estado', {
            'fields': ('presupuesto_maximo', 'estado', 'comentario_rechazo')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )