from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Mechanic
from django.contrib.auth.forms import AuthenticationForm

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