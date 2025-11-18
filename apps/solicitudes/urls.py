from django.urls import path
from . import views

app_name = 'solicitudes'

urlpatterns = [

    path('', views.lista_solicitudes, name='lista_solicitudes'),
    path('crear/', views.crear_solicitud, name='crear_solicitud'),
    path('<int:pk>/ver-pdf/', views.ver_pdf, name='ver_pdf'),
    path('<int:pk>/descargar-pdf/', views.descargar_pdf, name='descargar_pdf'),
     # Para jefes de proyecto (VALIDACIÓN)
    path('jefe/validar/', views.lista_solicitudes_jefe, name='validar_solicitudes'),
    path('jefe/<int:pk>/aprobar/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('jefe/<int:pk>/rechazar/', views.rechazar_solicitud, name='rechazar_solicitud'),
    # NUEVO: Para jefa de compras - ver solicitudes validadas
    path('compras/validadas/', views.lista_solicitudes_validadas, name='solicitudes_validadas'),
]