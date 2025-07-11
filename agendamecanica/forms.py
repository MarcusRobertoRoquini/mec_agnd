from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Mechanic, Vehicle, Category, Budget, BudgetItem, Service
from django.contrib.auth.forms import AuthenticationForm
import datetime
from django.forms import inlineformset_factory
from django.forms import modelformset_factory

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email','first_name', 'last_name', 'telefone', 'role', 'password1', 'password2']

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'autofocus': True}))


DIAS_SEMANA = [
    ('segunda', 'Segunda-feira'),
    ('terca', 'Terça-feira'),
    ('quarta', 'Quarta-feira'),
    ('quinta', 'Quinta-feira'),
    ('sexta', 'Sexta-feira'),
    ('sabado', 'Sábado'),
    ('domingo', 'Domingo'),
]

class MechanicForm(forms.ModelForm):
    specialties = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Especialidades",
        help_text="Selecione as especialidades do mecânico."
    )

    available_hours = forms.CharField(
        widget=forms.HiddenInput(),  # Será preenchido via JS
        required=False
    )

    class Meta:
        model = Mechanic
        fields = ['specialties', 'available_hours']
    


class VehicleForm(forms.ModelForm):
     class Meta:
        model = Vehicle
        fields = ['marca', 'modelo', 'ano', 'placa']

     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ano_atual = datetime.datetime.now().year
        self.fields['ano'].widget = forms.NumberInput(attrs={
            'min': 1900,
            'max': ano_atual + 1
        })



class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição geral ou observações do mecânico...'
            }),
        }
        labels = {
            'descricao': 'Descrição',
        }

class BudgetItemForm(forms.ModelForm):
    class Meta:
        model = BudgetItem
        fields = ['servico', 'preco_personalizado']
        widgets = {
            'servico': forms.Select(attrs={
                'class': 'form-control'
            }),
            'preco_personalizado': forms.TextInput(attrs={
                'class': 'form-control money-input',
                'placeholder': 'Preço personalizado (R$)'
            }),
        }
        labels = {
            'servico': 'Serviço',
            'preco_personalizado': 'Preço Personalizado (R$)',
        }

    def clean_preco_personalizado(self):
        data = self.cleaned_data.get('preco_personalizado')
        if data in (None, ''):
            raise forms.ValidationError("Este campo é obrigatório.")
        if isinstance(data, str):
            data = data.replace('.', '').replace(',', '.')
        try:
            return float(data)
        except ValueError:
            raise forms.ValidationError("Digite um valor numérico válido.")


BudgetItemFormSet = modelformset_factory(
    BudgetItem,
    fields=('servico', 'preco_personalizado'),
    extra=1,
    can_delete=True  # IMPORTANTE!
)
