from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Proveedor, Analitica, Trabajador

# ✅ Obtener el modelo de usuario personalizado correctamente
User = get_user_model()

class JefeProyectosTests(TestCase):
    
    def setUp(self):
        # Crear jefe de proyectos
        self.jefe_proyectos = User.objects.create_user(
            username='jefe_proyectos',
            password='testpass123',
            tipo_usuario='jefe_proyectos',
            esta_activo=True
        )
        
        # Crear usuario RH
        self.usuario_rh = User.objects.create_user(
            username='usuario_rh',
            password='testpass123',
            tipo_usuario='rh',
            esta_activo=True
        )
        
        # Crear usuario normal (sin permisos)
        self.usuario_normal = User.objects.create_user(
            username='usuario_normal',
            password='testpass123',
            tipo_usuario='solicitante'
        )
    
    def test_jefe_proyectos_puede_registrar_usuarios(self):
        """Test que verifica que jefe de proyectos puede registrar usuarios"""
        self.assertTrue(self.jefe_proyectos.puede_registrar_usuarios())
    
    def test_rh_no_puede_registrar_usuarios(self):
        """Test que verifica que RH NO puede registrar usuarios"""
        self.assertFalse(self.usuario_rh.puede_registrar_usuarios())
    
    def test_solicitante_no_puede_registrar_usuarios(self):
        """Test que verifica que solicitante NO puede registrar usuarios"""
        self.assertFalse(self.usuario_normal.puede_registrar_usuarios())
    
    def test_rh_puede_gestionar_analiticas(self):
        """Test que verifica que RH puede gestionar analíticas"""
        self.assertTrue(self.usuario_rh.puede_gestionar_analiticas())
    
    def test_jefe_proyectos_no_puede_gestionar_analiticas(self):
        """Test que verifica que jefe de proyectos NO puede gestionar analíticas"""
        self.assertFalse(self.jefe_proyectos.puede_gestionar_analiticas())

class UsuarioPersonalizadoTests(TestCase):
    
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            tipo_usuario='solicitante',
            telefono='1234567890',
            puesto='Analista'
        )
    
    def test_creacion_usuario(self):
        """Test de creación básica de usuario"""
        self.assertEqual(self.usuario.username, 'testuser')
        self.assertEqual(self.usuario.tipo_usuario, 'solicitante')
        self.assertTrue(self.usuario.check_password('testpass123'))
    
    def test_usuario_str_representation(self):
        """Test del método __str__ del usuario"""
        self.usuario.first_name = 'Juan'
        self.usuario.last_name = 'Pérez'
        self.assertEqual(
            str(self.usuario),
            'Juan Pérez - Usuario Solicitante'
        )
    
    def test_usuario_proveedor(self):
        """Test de usuario con rol proveedor"""
        usuario_proveedor = User.objects.create_user(
            username='proveedor_test',
            password='testpass123',
            tipo_usuario='proveedor'
        )
        self.assertTrue(usuario_proveedor.es_proveedor())
    
    def test_usuario_rh(self):
        """Test de usuario con rol RH"""
        usuario_rh = User.objects.create_user(
            username='rh_test',
            password='testpass123',
            tipo_usuario='rh'
        )
        self.assertTrue(usuario_rh.es_rh())

class AnaliticaTests(TestCase):
    
    def setUp(self):
        self.analitica = Analitica.objects.create(
            codigo='MX1234567',
            nombre='Mantenimiento Río Verde',
            descripcion='Proyecto de mantenimiento para la planta Río Verde',
            esta_activa=True
        )
    
    def test_creacion_analitica(self):
        """Test de creación básica de analítica"""
        self.assertEqual(self.analitica.codigo, 'MX1234567')
        self.assertEqual(self.analitica.nombre, 'Mantenimiento Río Verde')
        self.assertTrue(self.analitica.esta_activa)
    
    def test_analitica_str_representation(self):
        """Test del método __str__ de la analítica"""
        self.assertEqual(
            str(self.analitica),
            'MX1234567 - Mantenimiento Río Verde'
        )
    
    def test_analitica_unica(self):
        """Test que verifica que el código de analítica sea único"""
        with self.assertRaises(Exception):
            Analitica.objects.create(
                codigo='MX1234567',  # Mismo código
                nombre='Otro Proyecto',
                esta_activa=True
            )

class ProveedorTests(TestCase):
    
    def setUp(self):
        # Usar User (que es get_user_model()) en lugar de UsuarioPersonalizado directamente
        self.usuario_proveedor = User.objects.create_user(
            username='proveedor_user',
            password='testpass123',
            tipo_usuario='proveedor'
        )
        
        self.proveedor = Proveedor.objects.create(
            usuario=self.usuario_proveedor,
            rfc='XAXX010101000',
            razon_social='Empresa de Prueba SA de CV',
            direccion='Calle Falsa 123',
            numero_cuenta='1234567890',
            telefono_contacto='5551234567',
            email_contacto='contacto@empresa.com',
            terminos_pago=30
        )
    
    def test_creacion_proveedor(self):
        """Test de creación básica de proveedor"""
        self.assertEqual(self.proveedor.razon_social, 'Empresa de Prueba SA de CV')
        self.assertEqual(self.proveedor.rfc, 'XAXX010101000')
        self.assertEqual(self.proveedor.terminos_pago, 30)
    
    def test_relacion_usuario_proveedor(self):
        """Test de la relación OneToOne entre usuario y proveedor"""
        self.assertEqual(self.proveedor.usuario, self.usuario_proveedor)
        self.assertEqual(self.usuario_proveedor.proveedor, self.proveedor)
    
    def test_proveedor_str_representation(self):
        """Test del método __str__ del proveedor"""
        self.assertEqual(str(self.proveedor), 'Empresa de Prueba SA de CV')

class TrabajadorTests(TestCase):
    
    def setUp(self):
        self.trabajador = Trabajador.objects.create(
            first_name='Pedro',
            last_name='Gómez',
            rfc='GOMP780101XYZ', # <--- CAMBIADO A RFC
            puesto='Electricista',
            email='pedro.gomez@revergy.com',
            telefono='987654321'
        )
    
    def test_creacion_trabajador(self):
        """Test de creación básica de trabajador"""
        self.assertEqual(self.trabajador.first_name, 'Pedro')
        self.assertEqual(self.trabajador.rfc, 'GOMP780101XYZ') # <--- Verificación de RFC
        self.assertEqual(self.trabajador.get_full_name(), 'Pedro Gómez')
    
    def test_trabajador_str_representation(self):
        """Test del método __str__ del trabajador (incluye RFC)"""
        self.assertEqual(
            str(self.trabajador),
            'Pedro Gómez (GOMP780101XYZ)'
        )
    
    def test_rfc_unico(self):
        """Test que verifica que el RFC debe ser único"""
        with self.assertRaises(Exception): # Django lanzará IntegrityError o DatabaseError
            Trabajador.objects.create(
                first_name='Juan',
                last_name='Pérez',
                rfc='GOMP780101XYZ', # Mismo RFC, debe fallar
                puesto='Técnico',
            )