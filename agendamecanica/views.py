from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from .forms import CustomUserCreationForm, EmailAuthenticationForm, MechanicForm
from .models import Mechanic, Service, ServiceHistory, Budget, Appointment, Vehicle
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user.role == 'mecanico':
                user.aprovado = False
            user.save()
            auth_login(request, user)

            if user.role == 'mecanico':
                return redirect('cadastro_mecanico')  # Redireciona para segunda etapa de cadastro do mecanico

            return redirect('login') 
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            # Redirecionamento com base no papel do usuário
            if user.role == 'cliente':
                return redirect('clientehome')
            elif user.role == 'mecanico':
                return redirect('mecanicohome')
            else:
                return redirect('admin:index')  # ou outra página de admin

        else:
            messages.error(request, 'Email ou senha inválidos.')
    else:
        form = EmailAuthenticationForm()

    return render(request, 'login.html', {'form': form})




@login_required
def cadastro_mecanico(request):
    if not request.user.role == 'mecanico':
        return redirect('login')  # Apenas mecânicos devem acessar

    if hasattr(request.user, 'mechanic'):
        return redirect('login')  # Se já completou, não precisa repetir

    if request.method == 'POST':
        form = MechanicForm(request.POST)
        if form.is_valid():
            mechanic = form.save(commit=False)
            mechanic.user = request.user
            mechanic.save()
            return redirect('mecanicohome')  # Finaliza o cadastro
    else:
        form = MechanicForm()

    return render(request, 'cadastromec.html', {
        'mechanic_form': form,
        'user_form': None  
    })

@login_required
def cliente_home(request):
    user = request.user

    if user.role != 'cliente':
        return redirect('clientehome')  # segurança: só clientes acessam

    # Dados principais
    veiculos = user.vehicles.all()
    historico = ServiceHistory.objects.filter(vehicle__client=user)
    orcamentos = Budget.objects.filter(appointment__client=user)
    agendamentos = Appointment.objects.filter(client=user)

    context = {
        'cliente': user,
        'veiculos': veiculos,
        'historico': historico,
        'orcamentos': orcamentos,
        'agendamentos': agendamentos,
    }
    return render(request, 'clientehome.html', context)

@login_required
def mecanico_home(request):
    user = request.user

    if user.role != 'mecanico':
        return redirect('mecanicohome')  # segurança

    mechanic = user.mechanic

    hoje = timezone.now().date()
    semana = [hoje + timedelta(days=i) for i in range(7)]

    # Agendamentos do dia atual
    agendamentos_hoje = mechanic.appointments.filter(
        appointment_datetime__date=hoje
    ).select_related('client', 'vehicle', 'service')

    # Orçamentos respondidos (recentes)
    orcamentos_respondidos = mechanic.appointments.filter(
        budget__status__in=['aprovado', 'recusado']
    ).select_related('budget', 'client')

    # Agrupar agendamentos por dia 
    agendamentos_semanal = defaultdict(list)
    for agendamento in mechanic.appointments.filter(
        appointment_datetime__date__range=(hoje, hoje + timedelta(days=6))
    ):
        agendamentos_semanal[agendamento.appointment_datetime.date()].append(agendamento)

    # Histórico de serviços
    historico = mechanic.servicos_realizados.all()

    context = {
        'mecanico': mechanic,
        'especialidades': mechanic.specialties,
        'horarios': mechanic.available_hours,
        'agendamentos_hoje': agendamentos_hoje,
        'orcamentos_respondidos': orcamentos_respondidos,
        'agendamentos_semanal': dict(agendamentos_semanal),
        'historico': historico,
        'semana': semana,
    }
    return render(request, 'mechome.html', context)