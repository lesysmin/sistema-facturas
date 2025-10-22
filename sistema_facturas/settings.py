"""
Configuración para Sistema de Gestión de Facturas.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import sys
# Crear superusuario si no existe
from django.contrib.auth import get_user_model
from django.db import connections

# =============================================
# 1. CARGA DE VARIABLES DE ENTORNO
# =============================================

# Cargar variables del archivo .env
load_dotenv()

# =============================================
# 2. CONFIGURACIÓN DE PATHS
# =============================================

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Agregar apps al path (IMPORTANTE - mantener esto)
sys.path.append(os.path.join(BASE_DIR, 'apps'))

# =============================================
# 3. SEGURIDAD
# =============================================

# Clave secreta - OBLIGATORIA desde .env
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-clave-temporal-por-defecto')

# Modo depuración - desde .env
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Hosts permitidos - desde .env
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# =============================================
# 4. APLICACIONES INSTALADAS
# =============================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'guardian',

    # Third party apps (MANTENER)
    'crispy_forms',
    'crispy_bootstrap5',
    
    # Tus aplicaciones personalizadas (MANTENER estructura)
    'apps.core',
    'usuarios',  # Mantengo 'usuarios' (no 'apps.usuarios') por el AUTH_USER_MODEL
    'apps.solicitudes',
    'apps.cotizaciones',
    'apps.facturas', 
    'apps.reportes',
]

# =============================================
# 5. MIDDLEWARE
# =============================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# =============================================
# 6. CONFIGURACIÓN DE URLs Y TEMPLATES
# =============================================

ROOT_URLCONF = 'sistema_facturas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sistema_facturas.wsgi.application'

# =============================================
# 7. BASE DE DATOS
# =============================================

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': BASE_DIR / os.getenv('DB_NAME', 'db.sqlite3'),
    }
}

# =============================================
# 8. AUTENTICACIÓN Y AUTORIZACIÓN
# =============================================

# Backends de autenticación (AGREGAR ESTA SECCIÓN)
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # Backend por defecto de Django
    'guardian.backends.ObjectPermissionBackend',  # Backend de Guardian para permisos por objeto
)

# Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# =============================================
# 9. INTERNACIONALIZACIÓN
# =============================================

LANGUAGE_CODE = 'es-mx'  # MANTENER tu configuración
TIME_ZONE = 'America/Mexico_City'  # MANTENER tu configuración
USE_I18N = True
USE_TZ = True

# =============================================
# 10. ARCHIVOS ESTÁTICOS Y MEDIA
# =============================================

# Archivos estáticos (CSS, JS, imágenes)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise para producción
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Archivos media (PDFs, documentos subidos)
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')
MEDIA_ROOT = BASE_DIR / os.getenv('MEDIA_ROOT', 'media')

# =============================================
# 11. CONFIGURACIÓN DE EMAIL
# =============================================

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')

# =============================================
# 12. OTRAS CONFIGURACIONES IMPORTANTES (MANTENER)
# =============================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms (MANTENER)
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Modelo de usuario personalizado (MANTENER - MUY IMPORTANTE)
AUTH_USER_MODEL = 'usuarios.UsuarioPersonalizado'

# Configuración de login (MANTENER tu configuración)
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'

# =============================================
# 13. VERIFICACIÓN .env
# =============================================

# Mensajes de debug para verificar .env
if DEBUG:
    print("✅ .env cargado correctamente")
    print(f"✅ Entorno: {os.getenv('DJANGO_ENV', 'No especificado')}")
    print(f"✅ Debug: {DEBUG}")
    print(f"✅ User Model: {AUTH_USER_MODEL}")

# Esperar a que la base de datos esté lista
for conn in connections.all():
    if conn.is_usable():
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin', 
                email='admin@revergy.com',
                password='Admin123!'
            )
        break