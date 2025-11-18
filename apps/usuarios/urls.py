from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Registro por Jefe de Proyectos
    path('solicitantes/registro/', views.registro_solicitante, name='registro_solicitante'),
    path('solicitantes/', views.lista_solicitantes, name='lista_solicitantes'),
    path('solicitantes/editar/<int:usuario_id>/', views.editar_solicitante, name='editar_solicitante'),
    path('solicitantes/cambiar-estado/<int:usuario_id>/', views.cambiar_estado_solicitante, name='cambiar_estado_solicitante'),
   
    # Gestión de Trabajadores (Solo RH y admin)
    path('trabajadores/', views.lista_trabajadores, name='lista_trabajadores'),
    path('trabajadores/crear/', views.crear_trabajador, name='crear_trabajador'),
    path('trabajadores/<int:pk>/editar/', views.editar_trabajador, name='editar_trabajador'),

    # API ENDPOINTS PARA INTEGRACIÓN
    path('api/trabajadores/', views.listar_trabajadores_api, name='api_trabajadores'),
    path('api/usuarios-solicitantes/', views.listar_usuarios_solicitantes_api, name='api_usuarios_solicitantes'),
     path('api/user-info/<str:username>/', views.user_info_api, name='api_user_info'),

    # Gestión de analíticas (solo RH y admin)
    path('analiticas/', views.lista_analiticas, name='lista_analiticas'),
    path('analiticas/crear/', views.crear_analitica, name='crear_analitica'),
    path('analiticas/<int:pk>/editar/', views.editar_analitica, name='editar_analitica'),
    path('analiticas/<int:pk>/cambiar-estado/', views.cambiar_estado_analitica, name='cambiar_estado_analitica'),
    path('analiticas/<int:pk>/eliminar/', views.eliminar_analitica, name='eliminar_analitica'),
    
    # Gestión de proveedores (solo jefe de compras)
    path('proveedores/', views.lista_proveedores, name='lista_proveedores'),
    path('proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedores/<int:pk>/editar/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/<int:pk>/cambiar-estado/', views.cambiar_estado_proveedor, name='cambiar_estado_proveedor'),
    
    # Perfil de usuario - TEMPORALMENTE COMENTADO
    # path('perfil/', views.perfil_usuario, name='perfil_usuario'),
]