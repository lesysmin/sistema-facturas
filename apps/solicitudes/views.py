from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, HttpResponseNotFound
from django.conf import settings
import os
from .models import SolicitudCompra, ItemSolicitud
from .forms import SolicitudCompraForm
from django.utils import timezone

@login_required
def lista_solicitudes(request):
    """Listar solicitudes segun el tipo de usuario"""
    usuario = request.user
    
    if usuario.tipo_usuario == 'solicitante':
        solicitudes = SolicitudCompra.objects.filter(solicitante=usuario)
    elif usuario.tipo_usuario in ['jefe_proyectos', 'jefe_compras', 'admin_general']:
        solicitudes = SolicitudCompra.objects.all()
    else:
        solicitudes = SolicitudCompra.objects.none()
    
    context = {
        'solicitudes': solicitudes,
        'usuario': usuario
    }
    return render(request, 'solicitudes/lista.html', context)

@login_required
def crear_solicitud(request):
    """Crear nueva solicitud de compra"""
    if request.method == 'POST':
        form = SolicitudCompraForm(request.POST, request.FILES)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.solicitante = request.user
            solicitud.save()
            messages.success(request, f'Solicitud {solicitud.numero_sc} creada exitosamente.')
            return redirect('solicitudes:lista_solicitudes')
    else:
        form = SolicitudCompraForm()
    
    context = {'form': form}
    return render(request, 'solicitudes/crear.html', context)

@login_required
def detalle_solicitud(request, pk):
    """Ver detalles de una solicitud"""
    solicitud = get_object_or_404(SolicitudCompra, pk=pk)
    
    # Verificar permisos
    if (request.user.tipo_usuario == 'solicitante' and 
        solicitud.solicitante != request.user):
        messages.error(request, 'No tienes permisos para ver esta solicitud.')
        return redirect('solicitudes:lista_solicitudes')
    
    context = {'solicitud': solicitud}
    return render(request, 'solicitudes/detalle.html', context)

@login_required
def ver_pdf(request, pk):
    """Ver PDF de una solicitud"""
    solicitud = get_object_or_404(SolicitudCompra, pk=pk)
    
    # Verificar permisos
    if (request.user.tipo_usuario == 'solicitante' and 
        solicitud.solicitante != request.user):
        messages.error(request, 'No tienes permisos para ver esta solicitud.')
        return redirect('solicitudes:lista_solicitudes')
    
    if solicitud.archivo_pdf:
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, str(solicitud.archivo_pdf))
            if os.path.exists(file_path):
                return FileResponse(
                    open(file_path, 'rb'), 
                    content_type='application/pdf',
                    filename=f'{solicitud.numero_sc}.pdf'
                )
            else:
                messages.error(request, 'El archivo PDF no se encuentra en el servidor.')
                return redirect('solicitudes:detalle_solicitud', pk=pk)
        except Exception as e:
            messages.error(request, f'Error al abrir el PDF: {str(e)}')
            return redirect('solicitudes:detalle_solicitud', pk=pk)
    else:
        messages.error(request, 'No hay PDF disponible para esta solicitud.')
        return redirect('solicitudes:detalle_solicitud', pk=pk)

@login_required
def descargar_pdf(request, pk):
    """Descargar PDF de una solicitud"""
    solicitud = get_object_or_404(SolicitudCompra, pk=pk)
    
    # Verificar permisos
    if (request.user.tipo_usuario == 'solicitante' and 
        solicitud.solicitante != request.user):
        messages.error(request, 'No tienes permisos para descargar esta solicitud.')
        return redirect('solicitudes:lista_solicitudes')
    
    if solicitud.archivo_pdf:
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, str(solicitud.archivo_pdf))
            if os.path.exists(file_path):
                response = FileResponse(
                    open(file_path, 'rb'), 
                    content_type='application/pdf'
                )
                response['Content-Disposition'] = f'attachment; filename="{solicitud.numero_sc}.pdf"'
                return response
            else:
                messages.error(request, 'El archivo PDF no se encuentra en el servidor.')
                return redirect('solicitudes:detalle_solicitud', pk=pk)
        except Exception as e:
            messages.error(request, f'Error al descargar el PDF: {str(e)}')
            return redirect('solicitudes:detalle_solicitud', pk=pk)
    else:
        messages.error(request, 'No hay PDF disponible para esta solicitud.')
        return redirect('solicitudes:detalle_solicitud', pk=pk)
    
# AGREGAR ESTAS VISTAS AL FINAL DE TU ARCHIVO ACTUAL

@login_required
def lista_solicitudes_jefe(request):
    print("🟢 VISTA lista_solicitudes_jefe EJECUTÁNDOSE")

    """Vista para que los jefes de proyecto validen SC pendientes"""
    # Verificar que el usuario sea jefe de proyectos
    if request.user.tipo_usuario != 'jefe_proyectos':
        messages.error(request, 'No tienes permisos para acceder a esta función.')
        return redirect('solicitudes:lista_solicitudes')
    
    # SOLO solicitudes pendientes
    solicitudes = SolicitudCompra.objects.filter(
        estado='pendiente'
    ).order_by('-fecha_creacion')
    
    # Filtros
    prioridad_filter = request.GET.get('prioridad', '')
    proyecto_filter = request.GET.get('proyecto', '')
    
    if prioridad_filter:
        solicitudes = solicitudes.filter(prioridad=prioridad_filter)
    if proyecto_filter:
        solicitudes = solicitudes.filter(proyecto_id=proyecto_filter)
    
    context = {
        'solicitudes': solicitudes,
        'prioridad_filter': prioridad_filter,
        'proyecto_filter': proyecto_filter,
    }
    
    return render(request, 'solicitudes/lista_jefe.html', context)

@login_required
def aprobar_solicitud(request, **kwargs):
    """Vista para que el jefe de proyecto apruebe una solicitud - Versión genérica"""
    print(f"🟢 APROBAR - kwargs recibidos: {kwargs}")
    
    # Obtener el ID sin importar cómo venga en la URL
    pk = kwargs.get('pk')
    print(f"🟢 APROBAR - pk extraído: {pk}")
    
    if request.user.tipo_usuario != 'jefe_proyectos':
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('solicitudes:lista_solicitudes')
    
    solicitud = get_object_or_404(SolicitudCompra, pk=pk)
    
    if request.method == 'POST':
        comentarios = request.POST.get('comentarios', '')
        
        # Actualizar estado
        solicitud.estado = 'aprobada'
        solicitud.comentarios_decision = comentarios
        solicitud.fecha_decision = timezone.now()
        solicitud.save()
        
        messages.success(request, f'Solicitud {solicitud.numero_sc} aprobada correctamente.')
        return redirect('solicitudes:validar_solicitudes')
    
    return redirect('solicitudes:validar_solicitudes')

@login_required
def rechazar_solicitud(request, **kwargs):
    """Vista para que el jefe de proyecto rechace una solicitud - Versión genérica"""
    print(f"🔴 RECHAZAR - kwargs recibidos: {kwargs}")
    
    # Obtener el ID sin importar cómo venga en la URL
    pk = kwargs.get('pk')
    print(f"🔴 RECHAZAR - pk extraído: {pk}")
    
    if request.user.tipo_usuario != 'jefe_proyectos':
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('solicitudes:lista_solicitudes')
    
    solicitud = get_object_or_404(SolicitudCompra, pk=pk)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '')
        comentarios = request.POST.get('comentarios', '')
        
        if not motivo:
            messages.error(request, 'Debe seleccionar un motivo para el rechazo.')
            return redirect('solicitudes:validar_solicitudes')
        
        # Actualizar estado
        solicitud.estado = 'rechazada'
        solicitud.motivo_rechazo = motivo
        solicitud.comentarios_decision = comentarios
        solicitud.fecha_decision = timezone.now()
        solicitud.save()
        
        messages.success(request, f'Solicitud {solicitud.numero_sc} rechazada correctamente.')
        return redirect('solicitudes:validar_solicitudes')
    
    return redirect('solicitudes:validar_solicitudes')