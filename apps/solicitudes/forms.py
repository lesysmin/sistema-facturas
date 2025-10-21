from django import forms
from .models import SolicitudCompra, ItemSolicitud

class SolicitudCompraForm(forms.ModelForm):
    class Meta:
        model = SolicitudCompra
        fields = ['numero_sc', 'prioridad', 'codificacion', 'analitica', 'descripcion', 'archivo_pdf']
        widgets = {
            'numero_sc': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SC-2024-001',
                'autocomplete': 'off'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'codificacion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'analitica': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'MX1234567',
                'pattern': 'MX\d{7}',
                'title': 'Formato: MX seguido de 7 numeros',
                'autocomplete': 'off'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe detalladamente lo que necesitas comprar...'
            }),
            'archivo_pdf': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
        }
        help_texts = {
            'numero_sc': 'Ingrese un número único para la solicitud. Ejemplo: SC-2024-001',
            'codificacion': 'Seleccione la categoría de la compra',
            'analitica': 'Formato: MX seguido de 7 numeros. Ejemplo: MX1234567',
        }
        
        labels = {
            'numero_sc': 'Número de Solicitud',
            'prioridad': 'Prioridad',
            'codificacion': 'Codificación de Compra',
            'analitica': 'Analítica',
            'descripcion': 'Descripción Detallada',
            'archivo_pdf': 'Archivo PDF',
        }

    def clean_numero_sc(self):
        """Validar que el número de SC sea único"""
        numero_sc = self.cleaned_data.get('numero_sc')
        
        if numero_sc:
            # Verificar si ya existe (excluyendo la instancia actual si estamos editando)
            queryset = SolicitudCompra.objects.filter(numero_sc=numero_sc)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
                
            if queryset.exists():
                raise forms.ValidationError('Este número de solicitud ya existe. Por favor, use otro.')
            
            # Validar formato básico
            if not numero_sc.startswith('SC-'):
                raise forms.ValidationError('El número de solicitud debe comenzar con "SC-"')
                
        return numero_sc

    def clean_analitica(self):
        """Validar formato de analítica"""
        analitica = self.cleaned_data.get('analitica')
        
        if analitica:
            # Convertir a mayúsculas
            analitica = analitica.upper()
            
            # Validar formato
            import re
            pattern = r'^MX\d{7}$'
            if not re.match(pattern, analitica):
                raise forms.ValidationError('La analítica debe tener el formato MX seguido de 7 números. Ejemplo: MX1234567')
                
        return analitica