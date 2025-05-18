from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm

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
    return render(request, 'agendamecanica/register.html', {'form': form})
