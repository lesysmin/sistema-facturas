from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse  
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Q
from .models import UsuarioPersonalizado, Proveedor, Analitica, Trabajador
from .forms import RegistroSolicitanteForm, EditarSolicitanteForm, ProveedorForm, AnaliticaForm, TrabajadorForm

def listar_trabajadores_api(request):
    """
    API endpoint que devuelve lista de trabajadores en formato JSON
    Para integración con la aplicación de asistencia (Node.js)
    """
    try:
        # Obtener TODOS los trabajadores (sin filtrar por esta_activo)
        trabajadores = Trabajador.objects.all().values(
            'id', 
            'first_name', 
            'last_name', 
            'rfc',
            'puesto',
            'email',
            'telefono',
            'fecha_registro'  # Agregar fecha_registro si la necesitas
        )
        
        # Convertir QuerySet a lista
        data = list(trabajadores)
        
        # Agregar campo nombre_completo para facilidad de uso
        for trabajador in data:
            trabajador['nombre_completo'] = f"{trabajador['first_name']} {trabajador['last_name']}"
        
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        return JsonResponse(
            {'error': f'Error al obtener trabajadores: {str(e)}'}, 
            status=500
        )

def listar_usuarios_solicitantes_api(request):
    """
    API endpoint alternativo que devuelve usuarios solicitantes
    En caso de que prefieras usar UsuarioPersonalizado en lugar de Trabajador
    """
    try:
        # Filtrar usuarios solicitantes activos
        usuarios = UsuarioPersonalizado.objects.filter(
            tipo_usuario='solicitante',
            esta_activo=True
        ).values(
            'id',
            'first_name',
            'last_name', 
            'username',
            'rfc',
            'email'
        )
        
        data = list(usuarios)
        
        # Agregar nombre completo
        for usuario in data:
            usuario['nombre_completo'] = f"{usuario['first_name']} {usuario['last_name']}"
            
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        return JsonResponse(
            {'error': f'Error al obtener usuarios: {str(e)}'}, 
            status=500
        )
# ============================================================================
# VISTAS EXISTENTES (MANTENER SIN CAMBIOS)
# ============================================================================

@login_required
def perfil_usuario(request):
    """Vista para ver y editar perfil de usuario"""
    usuario = request.user
    return render(request, 'usuarios/perfil.html', {
        'usuario': usuario,
        'es_proveedor': hasattr(usuario, 'proveedor')
    })

@login_required
def registro_solicitante(request):
    """
    Vista para que Jefe de Proyectos registre nuevos usuarios Solicitantes
    """
    # Verificar permisos
    if not request.user.puede_registrar_usuarios():
        messages.error(request, 'No tiene permisos para registrar usuarios')
        return redirect('solicitudes:lista_solicitudes')
    
    if request.method == 'POST':
        form = RegistroSolicitanteForm(request.POST)
        if form.is_valid():
            try:
                solicitante = form.save()
                
                messages.success(
                    request, 
                    f'Usuario solicitante "{solicitante.get_full_name()}" registrado exitosamente. '
                    f'Credenciales: Usuario: {solicitante.username}'
                )
                return redirect('usuarios:lista_solicitantes')
                
            except Exception as e:
                messages.error(request, f'Error al registrar el usuario: {str(e)}')
    else:
        form = RegistroSolicitanteForm()
    
    return render(request, 'usuarios/registro_solicitante.html', {
        'form': form,
        'titulo': 'Registrar Nuevo Solicitante'
    })

@login_required
def lista_solicitantes(request):
    """
    Vista para listar todos los usuarios solicitantes
    """
    if not request.user.puede_registrar_usuarios():
        messages.error(request, 'No tiene permisos para ver esta lista')
        return redirect('solicitudes:lista_solicitudes')
    
    solicitantes = UsuarioPersonalizado.objects.filter(
        tipo_usuario='solicitante'
    ).order_by('-date_joined')
    
    return render(request, 'usuarios/lista_solicitantes.html', {
        'solicitantes': solicitantes
    })

@login_required
def editar_solicitante(request, usuario_id):
    """
    Vista para editar un usuario solicitante
    """
    if not request.user.puede_registrar_usuarios():
        messages.error(request, 'No tiene permisos para editar usuarios')
        return redirect('solicitudes:lista_solicitudes')
    
    solicitante = get_object_or_404(
        UsuarioPersonalizado, 
        id=usuario_id, 
        tipo_usuario='solicitante'
    )
    
    if request.method == 'POST':
        form = EditarSolicitanteForm(request.POST, instance=solicitante)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado exitosamente')
            return redirect('usuarios:lista_solicitantes')
    else:
        form = EditarSolicitanteForm(instance=solicitante)
    
    return render(request, 'usuarios/editar_solicitante.html', {
        'form': form,
        'solicitante': solicitante
    })

@login_required
def cambiar_estado_solicitante(request, usuario_id):
    """
    Vista para activar/desactivar un usuario solicitante
    """
    if not request.user.puede_registrar_usuarios():
        return HttpResponseForbidden("No tiene permisos para esta acción")
    
    solicitante = get_object_or_404(
        UsuarioPersonalizado, 
        id=usuario_id, 
        tipo_usuario='solicitante'
    )
    
    solicitante.esta_activo = not solicitante.esta_activo
    solicitante.save()
    
    estado = "activado" if solicitante.esta_activo else "desactivado"
    messages.success(request, f'Usuario {estado} exitosamente')
    
    return redirect('usuarios:lista_solicitantes')

# ============================================================================
# VISTAS PARA GESTIÓN DE ANALÍTICAS (SOLO RH Y ADMIN)
# ============================================================================

@login_required
def lista_analiticas(request):
    """Lista de analíticas - Solo RH y admin"""
    if not request.user.puede_gestionar_analiticas():
        messages.error(request, 'No tienes permisos para acceder a esta función.')
        return redirect('solicitudes:lista_solicitudes')
    
    analiticas = Analitica.objects.all().order_by('codigo')
    
    # Búsqueda
    search_query = request.GET.get('search', '')
    if search_query:
        analiticas = analiticas.filter(
            Q(codigo__icontains=search_query) |
            Q(nombre__icontains=search_query) |
            Q(descripcion__icontains=search_query)
        )
    
    # Filtro por estado
    activa_filter = request.GET.get('activa', '')
    if activa_filter:
        analiticas = analiticas.filter(esta_activa=(activa_filter == 'true'))
    
    context = {
        'analiticas': analiticas,
        'search_query': search_query,
        'activa_filter': activa_filter,
    }
    return render(request, 'usuarios/lista_analiticas.html', context)

@login_required
def crear_analitica(request):
    """Crear nueva analítica - Solo RH y admin"""
    if not request.user.puede_gestionar_analiticas():
        messages.error(request, 'No tienes permisos para acceder a esta función.')
        return redirect('solicitudes:lista_solicitudes')
    
    if request.method == 'POST':
        form = AnaliticaForm(request.POST)
        if form.is_valid():
            analitica = form.save()
            messages.success(request, f'Analítica {analitica.codigo} creada exitosamente.')
            return redirect('usuarios:lista_analiticas')
    else:
        form = AnaliticaForm()
    
    return render(request, 'usuarios/crear_analitica.html', {'form': form})

@login_required
def editar_analitica(request, pk):
    """Editar analítica - Solo RH y admin"""
    if not request.user.puede_gestionar_analiticas():
        messages.error(request, 'No tienes permisos para acceder a esta función.')
        return redirect('solicitudes:lista_solicitudes')
    
    analitica = get_object_or_404(Analitica, pk=pk)
    
    if request.method == 'POST':
        form = AnaliticaForm(request.POST, instance=analitica)
        if form.is_valid():
            analitica = form.save()
            messages.success(request, f'Analítica {analitica.codigo} actualizada exitosamente.')
            return redirect('usuarios:lista_analiticas')
    else:
        form = AnaliticaForm(instance=analitica)
    
    context = {'form': form, 'analitica': analitica}
    return render(request, 'usuarios/editar_analitica.html', context)

@login_required
def cambiar_estado_analitica(request, pk):
    """Activar/desactivar analítica - Solo RH y admin"""
    if not request.user.puede_gestionar_analiticas():
        return HttpResponseForbidden("No tiene permisos para esta acción")
    
    analitica = get_object_or_404(Analitica, pk=pk)
    analitica.esta_activa = not analitica.esta_activa
    analitica.save()
    
    estado = "activada" if analitica.esta_activa else "desactivada"
    messages.success(request, f'Analítica {estado} exitosamente')
    
    return redirect('usuarios:lista_analiticas')

@login_required
def eliminar_analitica(request, pk):
    """Eliminar analítica - Solo RH y admin"""
    if not request.user.puede_gestionar_analiticas():
        return HttpResponseForbidden("No tiene permisos para esta acción")
    
    analitica = get_object_or_404(Analitica, pk=pk)
    
    if request.method == 'POST':
        codigo = analitica.codigo
        analitica.delete()
        messages.success(request, f'Analítica {codigo} eliminada exitosamente.')
        return redirect('usuarios:lista_analiticas')
    
    return render(request, 'usuarios/eliminar_analitica.html', {'analitica': analitica})

@login_required
def lista_trabajadores(request):
    """Lista de trabajadores/recursos - Solo RH y admin"""
    if not request.user.puede_gestionar_analiticas():
        messages.error(request, 'No tienes permisos para acceder a esta función.')
        return redirect('solicitudes:lista_solicitudes')
    
    trabajadores = Trabajador.objects.all().order_by('last_name', 'first_name')
    
    # Búsqueda simple
    search_query = request.GET.get('search', '')
    if search_query:
        trabajadores = trabajadores.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(rfc__icontains=search_query) |
            Q(puesto__icontains=search_query)
        )
        
    context = {
        'trabajadores': trabajadores,
        'search_query': search_query,
    }
    return render(request, 'usuarios/lista_trabajadores.html', context)

@login_required
def crear_trabajador(request):
    """Crear nuevo trabajador/recurso - Solo RH y admin"""
    if not request.user.puede_gestionar_analiticas():
        messages.error(request, 'No tienes permisos para acceder a esta función.')
        return redirect('solicitudes:lista_solicitudes')
    
    if request.method == 'POST':
        form = TrabajadorForm(request.POST)
        if form.is_valid():
            trabajador = form.save()
            messages.success(request, f'Trabajador {trabajador.get_full_name()} registrado exitosamente.')
            return redirect('usuarios:lista_trabajadores')
        else:
            messages.error(request, 'Error en el formulario. Por favor, revise los campos.')
    else:
        form = TrabajadorForm()
    
    return render(request, 'usuarios/crear_trabajador.html', {'form': form})

@login_required
def editar_trabajador(request, pk):
    """Editar trabajador/recurso - Solo RH y admin"""
    if not request.user.puede_gestionar_analiticas():
        messages.error(request, 'No tienes permisos para acceder a esta función.')
        return redirect('solicitudes:lista_solicitudes')
    
    trabajador = get_object_or_404(Trabajador, pk=pk)
    
    if request.method == 'POST':
        form = TrabajadorForm(request.POST, instance=trabajador)
        if form.is_valid():
            form.save()
            messages.success(request, f'Trabajador {trabajador.get_full_name()} actualizado exitosamente.')
            return redirect('usuarios:lista_trabajadores')
    else:
        form = TrabajadorForm(instance=trabajador)
    
    context = {'form': form, 'trabajador': trabajador}
    return render(request, 'usuarios/editar_trabajador.html', context)

# ============================================================================
# VISTAS PARA GESTIÓN DE PROVEEDORES (SOLO JEFE DE COMPRAS)
# ============================================================================

@login_required
def lista_proveedores(request):
    """Lista de proveedores - Solo jefe de compras"""
    if not request.user.es_jefe_compras():
        messages.error(request, 'No tienes permisos para acceder a esta función.')
        return redirect('solicitudes:lista_solicitudes')
    
    proveedores = Proveedor.objects.all().order_by('razon_social')
    
    # Búsqueda
    search_query = request.GET.get('search', '')
    if search_query:
        proveedores = proveedores.filter(
            Q(numero_proveedor__icontains=search_query) |
            Q(razon_social__icontains=search_query) |
            Q(rfc__icontains=search_query) |
            Q(representante_legal__icontains=search_query)
        )
    
    # Filtros
    ambito_filter = request.GET.get('ambito', '')
    tipo_filter = request.GET.get('tipo', '')
    activo_filter = request.GET.get('activo', '')
    
    if ambito_filter:
        proveedores = proveedores.filter(ambito=ambito_filter)
    if tipo_filter:
        proveedores = proveedores.filter(tipo_proveedor=tipo_filter)
    if activo_filter:
        proveedores = proveedores.filter(esta_activo=(activo_filter == 'true'))
    
    context = {
        'proveedores': proveedores,
        'search_query': search_query,
        'ambito_filter': ambito_filter,
        'tipo_filter': tipo_filter,
        'activo_filter': activo_filter,
    }
    return render(request, 'usuarios/lista_proveedores.html', context)

@login_required
def crear_proveedor(request):
    """Crear nuevo proveedor - Solo jefe de compras"""
    print("🔵 VISTA crear_proveedor EJECUTÁNDOSE")
    
    if not request.user.es_jefe_compras():
        messages.error(request, 'No tienes permisos para acceder a esta función.')
        return redirect('solicitudes:lista_solicitudes')
    
    if request.method == 'POST':
        print("🔵 MÉTODO POST")
        form = ProveedorForm(request.POST)
        if form.is_valid():
            print("🔵 FORMULARIO VÁLIDO")
            proveedor = form.save()
            messages.success(request, f'Proveedor {proveedor.numero_proveedor} creado exitosamente.')
            return redirect('usuarios:lista_proveedores')
        else:
            print("🔵 FORMULARIO INVÁLIDO:", form.errors)
    else:
        print("🔵 MÉTODO GET - Mostrando formulario vacío")
        form = ProveedorForm()
    
    context = {'form': form}
    print("🔵 CONTEXT:", context)
    return render(request, 'usuarios/crear_proveedor.html', context)

@login_required
def editar_proveedor(request, pk):
    """Editar proveedor - Solo jefe de compras"""
    if not request.user.es_jefe_compras():
        messages.error(request, 'No tienes permisos para acceder a esta función.')
        return redirect('solicitudes:lista_solicitudes')
    
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            proveedor = form.save()
            messages.success(request, f'Proveedor {proveedor.numero_proveedor} actualizado exitosamente.')
            return redirect('usuarios:lista_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    
    context = {'form': form, 'proveedor': proveedor}
    return render(request, 'usuarios/editar_proveedor.html', context)

@login_required
def cambiar_estado_proveedor(request, pk):
    """Activar/desactivar proveedor - Solo jefe de compras"""
    if not request.user.es_jefe_compras():
        return HttpResponseForbidden("No tiene permisos para esta acción")
    
    proveedor = get_object_or_404(Proveedor, pk=pk)
    proveedor.esta_activo = not proveedor.esta_activo
    proveedor.save()
    
    estado = "activado" if proveedor.esta_activo else "desactivado"
    messages.success(request, f'Proveedor {estado} exitosamente')
    
    return redirect('usuarios:lista_proveedores')
@csrf_exempt
def user_info_api(request, username):
    """
    API endpoint para obtener información de usuario
    Para integración con la app de asistencia - SOLO RH
    """
    try:
        user = UsuarioPersonalizado.objects.get(username=username)
        
        # Información básica del usuario
        data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'tipo_usuario': user.tipo_usuario,
            'puesto': user.puesto,
            'telefono': user.telefono,
            'esta_activo': user.esta_activo,
            'is_rh': user.tipo_usuario == 'rh',
            'is_jefe_proyectos': user.tipo_usuario == 'jefe_proyectos',
            'is_jefe_compras': user.tipo_usuario == 'jefe_compras', 
            'is_admin': user.tipo_usuario == 'admin_general',
            'puede_acceder_asistencia': user.tipo_usuario in ['rh', 'admin_general']
        }
        
        return JsonResponse(data)
        
    except UsuarioPersonalizado.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def verify_credentials_api(request):
    """
    API endpoint para verificar credenciales de usuario de forma segura
    Para integración con la app de asistencia - SOLO RH
    """
    if request.method == 'POST':
        try:
            # Parsear el cuerpo de la solicitud
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            # Validaciones básicas
            if not username or not password:
                return JsonResponse({
                    'success': False,
                    'error': 'Username y password son requeridos'
                }, status=400)
            
            # Autenticar usuario con el sistema de Django
            user = authenticate(username=username, password=password)
            
            if user is not None and user.is_active:
                # Verificar que sea RH o admin
                if user.tipo_usuario not in ['rh', 'admin_general']:
                    return JsonResponse({
                        'success': False,
                        'error': 'Solo personal de Recursos Humanos puede acceder a esta aplicación'
                    }, status=403)
                
                # Devolver información del usuario
                user_info = {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'tipo_usuario': user.tipo_usuario,
                    'puesto': user.puesto,
                    'telefono': user.telefono,
                    'esta_activo': user.esta_activo,
                    'is_rh': user.tipo_usuario == 'rh',
                    'is_admin': user.tipo_usuario == 'admin_general'
                }
                
                return JsonResponse({
                    'success': True,
                    'user': user_info,
                    'message': 'Autenticación exitosa'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Credenciales inválidas o usuario inactivo'
                }, status=401)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Cuerpo de la solicitud JSON inválido'
            }, status=400)
        except Exception as e:
            print(f"Error en verify_credentials_api: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Error interno del servidor'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    }, status=405)