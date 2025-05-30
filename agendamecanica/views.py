from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from .forms import CustomUserCreationForm, EmailAuthenticationForm, MechanicForm, VehicleForm
from .models import Mechanic, Service, ServiceHistory, Budget, Appointment, Vehicle, Category
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, datetime
from collections import defaultdict
from django.contrib import messages
from django.contrib.auth import get_backends

from django.contrib.auth import login as auth_login
from django.contrib.auth import get_backends
from django.shortcuts import redirect, render
from .forms import CustomUserCreationForm
from .utils import gerar_horarios_disponiveis
from django.http import JsonResponse
import json

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            if user.role == 'mecanico':
                user.aprovado = False  # Mecânico precisa de aprovação manual

            user.save()

            # Login automático após cadastro
            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            auth_login(request, user)

            # Redirecionamento condicional
            if user.role == 'mecanico':
                return redirect('cadastro_mecanico')  # 2ª etapa do mecânico
            elif user.role == 'cliente':
                return redirect('cliente_home')  # Redireciona direto para home do cliente

            return redirect('login')  # Fallback para outros casos

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
                return redirect('cliente_home')
            elif user.role == 'mecanico':
                return redirect('mecanico_home')
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
        return redirect('login')

    if hasattr(request.user, 'mechanic'):
        return redirect('mecanico_home')

    if request.method == 'POST':
        form = MechanicForm(request.POST)
        available_hours_raw = request.POST.get('available_hours')
        try:
            available_hours = json.loads(available_hours_raw) if available_hours_raw else {}
        except json.JSONDecodeError:
            available_hours = {}
            messages.error(request, "Erro ao processar os horários. Tente novamente.")

        if form.is_valid():
            mechanic = form.save(commit=False)
            mechanic.user = request.user
            mechanic.available_hours = available_hours
            mechanic.save()
            form.save_m2m()  # Para salvar os dados ManyToMany (especialidades)
            return redirect('mecanico_home')
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
        return redirect('login')  # Segurança

    mechanic = user.mechanic
    hoje = timezone.now().date()
    semana = [hoje + timedelta(days=i) for i in range(7)]

    # Agendamentos de hoje
    agendamentos_hoje = mechanic.appointments.filter(
        appointment_datetime__date=hoje
    ).select_related('client', 'vehicle', 'service')

    # Orçamentos respondidos
    orcamentos_respondidos = mechanic.appointments.filter(
        budget__status__in=['aprovado', 'recusado']
    ).select_related('budget', 'client', 'service')

    # Agendamentos da semana
    agendamentos_semanal = defaultdict(list)
    for agendamento in mechanic.appointments.filter(
        appointment_datetime__date__range=(hoje, hoje + timedelta(days=6))
    ).select_related('service'):
        data_agendamento = agendamento.appointment_datetime.date()
        agendamentos_semanal[data_agendamento].append(agendamento)

    # Histórico de serviços realizados
    historico = mechanic.servicos_realizados.all().select_related('vehicle', 'service')

    context = {
        'mecanico': mechanic,
        'especialidades': mechanic.specialties.all(),  # ManyToMany para Category
        'horarios': mechanic.available_hours,
        'agendamentos_hoje': agendamentos_hoje,
        'orcamentos_respondidos': orcamentos_respondidos,
        'agendamentos_semanal': dict(agendamentos_semanal),
        'historico': historico,
        'semana': semana,
        'hoje': hoje.strftime('%d/%m/%Y'),
    }

    return render(request, 'mechome.html', context)

@login_required
def adicionar_veiculo(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            veiculo = form.save(commit=False)
            veiculo.client = request.user
            veiculo.save()
            return redirect('cliente_home')
    else:
        form = VehicleForm()
    return render(request, 'add_veiculo.html', {'form': form})

@login_required
def editar_veiculo(request, pk):
    veiculo = get_object_or_404(Vehicle, pk=pk, client=request.user)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=veiculo)
        if form.is_valid():
            form.save()
            return redirect('cliente_home')
    else:
        form = VehicleForm(instance=veiculo)
    return render(request, 'edit_veiculo.html', {'form': form, 'veiculo': veiculo})


@login_required
def iniciar_agendamento_view(request):
    user = request.user
    veiculos = Vehicle.objects.filter(client=user)
    categorias = Category.objects.all()
    servicos = Service.objects.all()

    if request.method == 'POST':
        veiculo_id = request.POST.get('veiculo')
        categoria_id = request.POST.get('categoria')
        servico_id = request.POST.get('servico')

        if not (veiculo_id and categoria_id and servico_id):
            messages.error(request, "Todos os campos são obrigatórios.")
            return redirect('iniciar_agendamento')

        return redirect('selecionar_mecanico', veiculo_id=veiculo_id, categoria_id=categoria_id, servico_id=servico_id)

    return render(request, 'iniciar_agendamento.html', {
        'veiculos': veiculos,
        'categorias': categorias,
        'servicos': servicos
    })



@login_required
def selecionar_mecanico(request, veiculo_id, categoria_id, servico_id):
    servico = get_object_or_404(Service, id=servico_id)
    veiculo = get_object_or_404(Vehicle, id=veiculo_id, client=request.user)

    mecanicos = Mechanic.objects.filter(specialties__id=categoria_id, user__aprovado=True)

    request.session['agendamento_dados'] = {
        'veiculo_id': veiculo_id,
        'categoria_id': categoria_id,
        'servico_id': servico_id,
    }

    return render(request, 'selecionar_mecanico.html', {
        'mecanicos': mecanicos,
        'servico': servico,
        'veiculo': veiculo
    })


@login_required
def horarios_disponiveis(request, mecanico_id):
    mecanico = get_object_or_404(Mechanic, id=mecanico_id)
    horarios = gerar_horarios_disponiveis(mecanico)
    return JsonResponse({'horarios': horarios})

@login_required
def servicos_por_categoria(request, categoria_id):
    servicos = Service.objects.filter(categoria_id=categoria_id).values('id', 'nome')
    return JsonResponse({'servicos': list(servicos)})