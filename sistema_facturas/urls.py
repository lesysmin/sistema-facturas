from django.contrib import admin
from django.urls import path, include 
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import dashboard, protected_media  # ← Asegúrate de importar protected_media

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('solicitudes/', include('apps.solicitudes.urls')),
    
    # ✅ Ruta PROTEGIDA para archivos media - SIEMPRE activa
     path('protected-media/<path:file_path>', protected_media, name='protected_media'),
]

# ✅ Solo en desarrollo, servir archivos estáticos
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()