from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate
from .forms import CustomUserCreationForm, EmailAuthenticationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user.role == 'mecanico':
                user.aprovado = False  # mecânico espera aprovação
            user.save()
            login(request, user)
            return redirect('home')  # redirecione para uma página inicial
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login(request):
    if request.method == "POST":
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')  # ou onde quiser redirecionar
    else:
        form = EmailAuthenticationForm()
    return render(request, 'login.html', {'form': form})