from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UsuarioPersonalizado, Proveedor, Analitica, Trabajador

class RegistroSolicitanteForm(forms.ModelForm):
    """Form para que Jefe de Proyectos registre Solicitantes"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="La contraseña será encriptada automáticamente"
    )
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = UsuarioPersonalizado
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'telefono', 'puesto', 'password'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'puesto': forms.TextInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Letras, números y @/./+/-/_ solamente.',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmar_password = cleaned_data.get("confirmar_password")
        
        if password and confirmar_password and password != confirmar_password:
            self.add_error('confirmar_password', "Las contraseñas no coinciden")
        
        return cleaned_data
    
    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password"])
        usuario.tipo_usuario = 'solicitante'  # Siempre será solicitante
        usuario.esta_activo = True  # Activado por defecto
        
        if commit:
            usuario.save()
        return usuario

class EditarSolicitanteForm(forms.ModelForm):
    """Form para editar solicitantes (sin cambiar tipo_usuario)"""
    class Meta:
        model = UsuarioPersonalizado
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'telefono', 'puesto', 'esta_activo'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'puesto': forms.TextInput(attrs={'class': 'form-control'}),
            'esta_activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AnaliticaForm(forms.ModelForm):
    """Form para gestionar analíticas"""
    class Meta:
        model = Analitica
        fields = ['codigo', 'nombre', 'descripcion', 'esta_activa']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'MX1234567'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mantenimiento Río Verde'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada del proyecto...'
            }),
            'esta_activa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        help_texts = {
            'codigo': 'Código único del proyecto (ej: MX1234567)',
            'nombre': 'Nombre descriptivo del proyecto',
        }
    
    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if codigo:
            # Verificar que sea único
            queryset = Analitica.objects.filter(codigo=codigo)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
                
            if queryset.exists():
                raise forms.ValidationError('Este código de analítica ya existe.')
                
        return codigo
    
class TrabajadorForm(forms.ModelForm):
    """Form para que RH registre nuevos trabajadores/recursos"""
    class Meta:
        model = Trabajador
        fields = [
            'first_name', 'last_name', 'rfc', 'puesto', 
            'email', 'telefono'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'rfc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RFC123456XYZ'}), # <--- CAMBIADO
            'puesto': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_rfc(self): # <--- VALIDACIÓN DE RFC
        rfc = self.cleaned_data.get('rfc')
        if rfc:
            rfc = rfc.upper().strip() # Normalizar
            # Verificar que sea único
            queryset = Trabajador.objects.filter(rfc=rfc)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
                
            if queryset.exists():
                raise forms.ValidationError('Este RFC ya se encuentra registrado para otro trabajador.')
                
        return rfc

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'numero_proveedor', 'rfc', 'cedula_situacion_fiscal', 'razon_social', 
            'direccion_fiscal', 'banco', 'numero_cuenta', 'clabe_interbancaria', 
            'swift_code', 'representante_legal', 'curp_representante', 
            'telefono_contacto', 'email_contacto', 'telefono_emergencia',
            'ambito', 'tipo_proveedor', 'cartera_servicios', 'terminos_pago', 'esta_activo'
        ]
        widgets = {
            'numero_proveedor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'PROV-2024-001'
            }),
            'rfc': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ABC123456XYZ'
            }),
            'cedula_situacion_fiscal': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'razon_social': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'direccion_fiscal': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'banco': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'numero_cuenta': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'clabe_interbancaria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '18 dígitos'
            }),
            'swift_code': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'representante_legal': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'curp_representante': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'telefono_contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '555-123-4567'
            }),
            'email_contacto': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'telefono_emergencia': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'ambito': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo_proveedor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cartera_servicios': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describa los productos o servicios que ofrece...'
            }),
            'terminos_pago': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'esta_activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        help_texts = {
            'numero_proveedor': 'Ejemplo: PROV-2024-001',
            'rfc': '13 caracteres para personas morales, 12 para físicas',
            'clabe_interbancaria': '18 dígitos para transferencias nacionales',
            'swift_code': 'Código para transferencias internacionales',
        }
    
    def clean_numero_proveedor(self):
        numero_proveedor = self.cleaned_data.get('numero_proveedor')
        if numero_proveedor:
            # Verificar que sea único
            queryset = Proveedor.objects.filter(numero_proveedor=numero_proveedor)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
                
            if queryset.exists():
                raise forms.ValidationError('Este número de proveedor ya existe.')
                
        return numero_proveedor
    
    def clean_rfc(self):
        rfc = self.cleaned_data.get('rfc')
        if rfc:
            # Validar formato básico de RFC
            rfc = rfc.upper().strip()
            if len(rfc) not in [12, 13]:
                raise forms.ValidationError('El RFC debe tener 12 o 13 caracteres.')
                
        return rfc