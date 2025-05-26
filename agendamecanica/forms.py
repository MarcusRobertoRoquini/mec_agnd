from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Mechanic, Vehicle
from django.contrib.auth.forms import AuthenticationForm
import datetime

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email','first_name', 'last_name', 'telefone', 'role', 'password1', 'password2']

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'autofocus': True}))


class MechanicForm(forms.ModelForm):
    specialties = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Ex: freios, motor, suspensão'}),
        help_text='Separe as especialidades por vírgula.'
    )
    available_hours = forms.JSONField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': '{"segunda": ["08:00-12:00", "13:00-17:00"]}'}),
        help_text='Insira os horários disponíveis no formato JSON. Ex: {"segunda": ["08:00-12:00"]}'
    )

    class Meta:
        model = Mechanic
        fields = ['specialties', 'available_hours']

    def clean_specialties(self):
        data = self.cleaned_data['specialties']
        return [item.strip() for item in data.split(',') if item.strip()]
    


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