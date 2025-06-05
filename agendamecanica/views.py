from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from .forms import CustomUserCreationForm, EmailAuthenticationForm, MechanicForm, VehicleForm, BudgetForm, BudgetItemForm
from .models import Mechanic, Service, ServiceHistory, Budget, Appointment, Vehicle, Category, BudgetItem
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, datetime
from collections import defaultdict
from django.contrib import messages
from django.contrib.auth import get_backends
from django.forms import modelformset_factory
from django.contrib.auth import login as auth_login
from django.contrib.auth import get_backends
from django.shortcuts import redirect, render
from .forms import CustomUserCreationForm
from .utils import gerar_horarios_disponiveis
from django.http import JsonResponse
import json
from django.utils.timezone import make_aware, is_naive
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_datetime
from django.template.loader import render_to_string

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

    # Garantir que apenas clientes acessem esta página
    if user.role != 'cliente':
        return redirect('login')  # ou 'home' se houver uma página inicial segura

    # Coleta de dados
    veiculos = user.vehicles.all()
    historico = ServiceHistory.objects.filter(vehicle__client=user).order_by('-data_realizacao')
    orcamentos = Budget.objects.filter(appointment__client=user).order_by('-id')  # ou .order_by('-criado_em') se tiver o campo
    agendamentos = Appointment.objects.filter(client=user).order_by('appointment_datetime')

    # Contexto passado para o template
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
    # Salva os dados na sessão para serem usados na confirmação
    request.session['veiculo_id'] = veiculo_id
    request.session['servico_id'] = servico_id

    categoria = get_object_or_404(Category, id=categoria_id)
    servico = get_object_or_404(Service, id=servico_id)
    veiculo = get_object_or_404(Vehicle, id=veiculo_id)

    # Busca mecânicos que tenham a especialidade correspondente à categoria
    mecanicos = Mechanic.objects.filter(specialties=categoria)

    return render(request, 'selecionar_mecanico.html', {
        'mecanicos': mecanicos,
        'servico': servico,
        'veiculo': veiculo
    })


@login_required
def horarios_disponiveis(request, mecanico_id):
    mecanico = get_object_or_404(Mechanic, id=mecanico_id)
    eventos = gerar_horarios_disponiveis(mecanico, dias_adiantados=30)
    return JsonResponse(eventos, safe=False)



@login_required
def servicos_por_categoria(request, categoria_id):
    servicos = Service.objects.filter(categoria_id=categoria_id).values('id', 'nome')
    return JsonResponse({'servicos': list(servicos)})

@login_required
@require_POST
def confirmar_agendamento(request):
    print("CONFIRMAR AGENDAMENTO CHAMADO")

    horario_str = request.POST.get('horario')
    mecanico_id = request.POST.get('mecanicoId')
    servico_id = request.session.get('servico_id')
    veiculo_id = request.session.get('veiculo_id')

    print("DEBUG Dados recebidos:")
    print("horario:", horario_str)
    print("mecanico_id:", mecanico_id)
    print("servico_id (sessão):", servico_id)
    print("veiculo_id (sessão):", veiculo_id)

    if not (horario_str and mecanico_id and servico_id and veiculo_id):
        messages.error(request, "Dados incompletos para confirmação de agendamento.")
        return redirect('cliente_home')
    

    try:
        horario = parse_datetime(horario_str)
        if horario is None:
            raise ValueError("Formato de data inválido.")

        # Torna timezone-aware se for naive
        if is_naive(horario):
            horario = make_aware(horario)

    except Exception as e:
        print("Erro ao converter horário:", e)
        messages.error(request, "Horário inválido.")
        return redirect('cliente_home')

    mecanico = get_object_or_404(Mechanic, id=mecanico_id)
    servico = get_object_or_404(Service, id=servico_id)
    veiculo = get_object_or_404(Vehicle, id=veiculo_id)

    if Appointment.objects.filter(mechanic=mecanico, appointment_datetime=horario).exists():
        messages.error(request, "Este horário já foi agendado por outro cliente.")
        return redirect('cliente_home')

    try:
        agendamento = Appointment.objects.create(
            client=request.user,
            mechanic=mecanico,
            service=servico,
            vehicle=veiculo,
            appointment_datetime=horario,
            status='pendente'
        )
        print("✅ AGENDAMENTO CRIADO:", agendamento.id)
    except Exception as e:
        print("❌ Erro ao criar agendamento:", e)
        messages.error(request, "Erro ao criar agendamento.")
        return redirect('cliente_home')

    # Limpa dados da sessão
    request.session.pop('servico_id', None)
    request.session.pop('veiculo_id', None)

    messages.success(request, "Agendamento confirmado com sucesso!")
    return render(request, 'confirmacao_agendamento.html', {
        'agendamento': agendamento
    }) 

@login_required
def atualizar_status(request, agendamento_id, novo_status):
    appointment = get_object_or_404(Appointment, id=agendamento_id)

    # Verifica se o usuário é o mecânico responsável
    if request.user != appointment.mechanic.user:
        messages.error(request, "Você não tem permissão para alterar este agendamento.")
        return redirect('mecanico_home')

    if novo_status in dict(Appointment.STATUS_CHOICES):
        appointment.status = novo_status
        appointment.save()
        messages.success(request, "Status atualizado com sucesso.")
    else:
        messages.error(request, "Status inválido.")

    return redirect('mecanico_home')


@login_required
def criar_orcamento(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if not hasattr(request.user, 'mechanic') or appointment.mechanic != request.user.mechanic:
        messages.error(request, "Você não tem permissão para criar orçamento para este agendamento.")
        return redirect('mecanico_home')

    BudgetItemFormSet = modelformset_factory(BudgetItem, form=BudgetItemForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = BudgetForm(request.POST)
        formset = BudgetItemFormSet(request.POST, queryset=BudgetItem.objects.none())

        if form.is_valid() and formset.is_valid():
            budget = form.save(commit=False)
            budget.appointment = appointment
            budget.status = 'enviado'
            budget.save()  # salva para criar o ID

            for item_form in formset:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE'):
                    item = item_form.save(commit=False)
                    item.budget = budget
                    item.save()

            # Atualiza total agora com os itens salvos
            budget.total = budget.calcular_total()
            budget.save()

            messages.success(request, "Orçamento criado e enviado ao cliente.")
            return redirect('mecanico_home')
    else:
        form = BudgetForm()
        formset = BudgetItemFormSet(queryset=BudgetItem.objects.none())

    return render(request, 'criar_orcamento.html', {
        'form': form,
        'formset': formset,
        'appointment': appointment
    })

@login_required
def ver_orcamento(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Verifica se o orçamento existe
    if hasattr(appointment, 'budget'):
        budget = appointment.budget
        html = render_to_string('partials/orcamento_detalhado.html', {
            'orcamento': budget,
        }, request=request)
        return JsonResponse({'html': html})
    else:
        return JsonResponse({'html': '<p>Orçamento ainda não disponível.</p>'})