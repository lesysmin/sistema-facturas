from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.conf import settings
from apps.solicitudes.models import SolicitudCompra
import os

@login_required
def dashboard(request):
    """
    Vista principal del dashboard que muestra modulos segun el rol
    y estadísticas con gráfica
    """
    user = request.user
    
    # CALCULAR ESTADÍSTICAS PARA LA GRÁFICA
    if user.tipo_usuario == 'solicitante':
        solicitudes = SolicitudCompra.objects.filter(solicitante=user)
    elif user.tipo_usuario in ['jefe_proyectos', 'jefe_compras', 'admin_general']:
        solicitudes = SolicitudCompra.objects.all()
    else:
        solicitudes = SolicitudCompra.objects.none()
    
    # Calcular estadísticas
    total_solicitudes = solicitudes.count()
    solicitudes_aprobadas = solicitudes.filter(estado='aprobada').count()
    solicitudes_rechazadas = solicitudes.filter(estado='rechazada').count()
    solicitudes_proceso = solicitudes.filter(estado__in=['pendiente', 'revision', 'aprobada_jefe']).count()
    
    # DEFINIR MÓDULOS POR ROL (tu código existente)
    modulos_por_rol = {
        'admin_general': [
            {
                'nombre': 'Gestion de Usuarios',
                'icono': 'fas fa-users-cog',
                'descripcion': 'Administrar todos los usuarios del sistema',
                'url': '/admin/usuarios/usuariopersonalizado/',
                'color': 'primary',
                'casos_uso': ['CU5: Gestionar Usuarios (CRUD)', 'CU23: Visualizar Registro de Todos los Actores', 'CU24: Acceder a Todos los Modulos']
            },
            {
                'nombre': 'Solicitudes de Compra',
                'icono': 'fas fa-file-alt',
                'descripcion': 'Gestionar todas las solicitudes de compra',
                'url': '#',
                'color': 'success',
                'casos_uso': ['CU6: Crear SC', 'CU7: Validar/Rechazar SC', 'CU8: Consultar Historial SC', 'CU9: Notificar Estado']
            },
            {
                'nombre': 'Cotizaciones y oC',
                'icono': 'fas fa-handshake',
                'descripcion': 'Gestion de cotizaciones y ordenes de compra',
                'url': '#',
                'color': 'info',
                'casos_uso': ['CU10: Solicitar Cotizaciones', 'CU11: Recibir Cotizaciones', 'CU12: Generar OC', 'CU13: Confirmar OC']
            },
            {
                'nombre': 'Gestion de Facturas',
                'icono': 'fas fa-receipt',
                'descripcion': 'Control de facturas y pagos',
                'url': '#',
                'color': 'warning',
                'casos_uso': ['CU14: Subir Factura', 'CU15: Consultar Facturas', 'CU16: Registrar Pago', 'CU17: Subir Comprobante']
            },
            {
                'nombre': 'Reportes',
                'icono': 'fas fa-chart-bar',
                'descripcion': 'Reportes y analisis del sistema',
                'url': '#',
                'color': 'dark',
                'casos_uso': ['CU20: Reporte Semanal/Mensual', 'CU21: Gastos por Proveedor', 'CU22: Deudas Pendientes']
            }
        ],
        'solicitante': [
            {
                'nombre': 'Mis Solicitudes',
                'icono': 'fas fa-file-alt',
                'descripcion': 'Crear y consultar mis solicitudes de compra',
                'url': '{% url "solicitudes:lista_solicitudes" %}',
                'color': 'primary',
                'casos_uso': ['CU1: Registrarse como Usuario Solicitante', 'CU6: Crear Solicitud de Compra', 'CU8: Consultar Mis SC']
            },
            {
                'nombre': 'Estado de Solicitudes',
                'icono': 'fas fa-tasks',
                'descripcion': 'Seguimiento del estado de mis solicitudes',
                'url': '{% url "solicitudes:lista_solicitudes" %}',
                'color': 'info',
                'casos_uso': ['CU8: Consultar Historial SC', 'CU9: Notificar Estado de Solicitud']
            }
        ],
        'jefe_proyectos': [
            {
                'nombre': 'Validar Solicitudes',
                'icono': 'fas fa-check-circle',
                'descripcion': 'Revisar y validar solicitudes de compra',
                'url': '#',
                'color': 'success',
                'casos_uso': ['CU7: Validar/Rechazar Solicitud de Compra', 'CU8: Consultar Historial SC']
            },
            {
                'nombre': 'Seguimiento Facturas',
                'icono': 'fas fa-receipt',
                'descripcion': 'Consultar facturas de mis proyectos',
                'url': '#',
                'color': 'warning',
                'casos_uso': ['CU15: Consultar Facturas Relacionadas']
            },
            {
                'nombre': 'Reportes',
                'icono': 'fas fa-chart-bar',
                'descripcion': 'Reportes de proyectos y gastos',
                'url': '#',
                'color': 'info',
                'casos_uso': ['CU20: Generar Reportes', 'CU21: Analizar Gastos']
            }
        ],
        'jefe_compras': [
            {
                'nombre': 'Validar Registros',
                'icono': 'fas fa-user-check',
                'descripcion': 'Validar registro de usuarios y proveedores',
                'url': '#',
                'color': 'primary',
                'casos_uso': ['CU2: Validar Usuario Solicitante', 'CU4: Validar Registro de Proveedor']
            },
            {
                'nombre': 'Gestion Cotizaciones',
                'icono': 'fas fa-handshake',
                'descripcion': 'Solicitar y gestionar cotizaciones',
                'url': '#',
                'color': 'success',
                'casos_uso': ['CU10: Solicitar Cotizaciones', 'CU12: Generar OC']
            },
            {
                'nombre': 'Gestion Facturas',
                'icono': 'fas fa-receipt',
                'descripcion': 'Gestionar facturas y pagos',
                'url': '#',
                'color': 'warning',
                'casos_uso': ['CU15: Consultar Facturas', 'CU16: Registrar Pago', 'CU17: Subir Comprobante', 'CU18: Pagos Parciales']
            },
            {
                'nombre': 'Reportes Compras',
                'icono': 'fas fa-chart-line',
                'descripcion': 'Reportes de compras y proveedores',
                'url': '#',
                'color': 'info',
                'casos_uso': ['CU20: Reportes Periodicos', 'CU21: Gastos por Proveedor']
            }
        ],
        'jefe_financiero': [
            {
                'nombre': 'Seguimiento Pagos',
                'icono': 'fas fa-money-bill-wave',
                'descripcion': 'Control y seguimiento de pagos',
                'url': '#',
                'color': 'success',
                'casos_uso': ['CU15: Consultar Facturas', 'CU16: Registrar Pago', 'CU18: Pagos Parciales']
            },
            {
                'nombre': 'Reportes Financieros',
                'icono': 'fas fa-chart-pie',
                'descripcion': 'Reportes financieros y de gastos',
                'url': '#',
                'color': 'info',
                'casos_uso': ['CU20: Reportes Periodicos', 'CU21: Gastos por Proveedor', 'CU22: Deudas Pendientes']
            }
        ],
        'proveedor': [
            {
                'nombre': 'Mis Cotizaciones',
                'icono': 'fas fa-file-invoice-dollar',
                'descripcion': 'Gestionar mis cotizaciones',
                'url': '#',
                'color': 'primary',
                'casos_uso': ['CU3: Registrarse como Proveedor', 'CU11: Recibir Cotizaciones', 'CU13: Confirmar OC']
            },
            {
                'nombre': 'Mis Facturas',
                'icono': 'fas fa-receipt',
                'descripcion': 'Subir y consultar mis facturas',
                'url': '#',
                'color': 'success',
                'casos_uso': ['CU14: Subir Factura', 'CU15: Consultar Facturas', 'CU19: Consultar Estado de Pago']
            },
            {
                'nombre': 'Estado de Pagos',
                'icono': 'fas fa-search-dollar',
                'descripcion': 'Consultar estado de mis pagos',
                'url': '#',
                'color': 'info',
                'casos_uso': ['CU19: Consultar Estado de Pago']
            }
        ]
    }
    
    modulos_usuario = modulos_por_rol.get(user.tipo_usuario, [])
    
    context = {
        'user': user,
        'titulo': 'Dashboard Principal',
        'modulos': modulos_usuario,
        'total_modulos': len(modulos_usuario),
        # Datos para la gráfica
        'total_solicitudes': total_solicitudes,
        'solicitudes_aceptadas': solicitudes_aprobadas, 
        'solicitudes_rechazadas': solicitudes_rechazadas,
        'solicitudes_proceso': solicitudes_proceso,
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def protected_media(request, file_path):
    """
    Vista para servir archivos media solo a usuarios autenticados
    y con permisos específicos
    """
    # Construir la ruta completa del archivo
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    
    # Verificar que el archivo existe
    if not os.path.exists(full_path):
        raise Http404("Archivo no encontrado")
    
    # VERIFICACIÓN DE PERMISOS ESPECÍFICOS
    # Para archivos PDF de solicitudes
    if 'solicitudes/pdf/' in file_path:
        try:
            # Extraer el nombre del archivo
            filename = os.path.basename(file_path)
            
            # Buscar la solicitud que tenga este archivo
            # Asumiendo que el campo se llama 'archivo_pdf' en tu modelo SolicitudCompra
            solicitud = SolicitudCompra.objects.get(archivo_pdf__contains=filename)
            
            # Verificar permisos:
            # - El solicitante puede ver sus propios archivos
            # - Los jefes y admin pueden ver todos los archivos
            # - Otros usuarios no pueden ver archivos ajenos
            user = request.user
            if user.tipo_usuario == 'solicitante' and user != solicitud.solicitante:
                raise Http404("No tienes permiso para ver este archivo")
                
            # Si el usuario es jefe_proyectos, jefe_compras o admin_general, puede ver todo
            elif user.tipo_usuario not in ['jefe_proyectos', 'jefe_compras', 'admin_general'] and user != solicitud.solicitante:
                raise Http404("No tienes permiso para ver este archivo")
                
        except SolicitudCompra.DoesNotExist:
            # Si no encontramos la solicitud, permitimos el acceso pero podrías restringirlo
            pass
    
    # Determinar el tipo de contenido basado en la extensión del archivo
    content_type = 'application/octet-stream'  # Por defecto
    
    if file_path.lower().endswith('.pdf'):
        content_type = 'application/pdf'
    elif file_path.lower().endswith(('.jpg', '.jpeg')):
        content_type = 'image/jpeg'
    elif file_path.lower().endswith('.png'):
        content_type = 'image/png'
    elif file_path.lower().endswith(('.doc', '.docx')):
        content_type = 'application/msword'
    
    # Servir el archivo
    with open(full_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type=content_type)
        
        # Configurar para visualización en el navegador en lugar de descarga
        if content_type.startswith(('application/pdf', 'image/')):
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
        else:
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            
        return response