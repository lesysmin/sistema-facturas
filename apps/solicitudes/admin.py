from django.contrib import admin
from .models import SolicitudCompra, ItemSolicitud

class ItemSolicitudInline(admin.TabularInline):
    model = ItemSolicitud
    extra = 1
    fields = ['descripcion', 'cantidad', 'precio_unitario', 'precio_total']
    readonly_fields = ['precio_total']

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
    inlines = [ItemSolicitudInline]
    
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

@admin.register(ItemSolicitud)
class ItemSolicitudAdmin(admin.ModelAdmin):
    list_display = [
        'solicitud', 
        'descripcion', 
        'cantidad', 
        'precio_unitario', 
        'precio_total'
    ]
    list_filter = ['solicitud__estado', 'solicitud__prioridad']
    search_fields = ['descripcion', 'solicitud__numero_sc']