from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime
from datetime import timedelta
from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField

class User(AbstractUser):
    email = models.EmailField('email address', unique=True)
    ROLES = (
        ('cliente', 'Cliente'),
        ('mecanico', 'Mecânico'),
        ('admin', 'Administrador'),
    )
    telefone = models.CharField(max_length=20)
    role = models.CharField(max_length=10, choices=ROLES)
    aprovado = models.BooleanField(default=False)  # para aprovação de mecânicos

class Vehicle(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vehicles'
    )
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    ano = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(datetime.datetime.now().year + 1)  # permite até o ano seguinte
        ]
    )
    placa = models.CharField(max_length=20, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.placa})"

    class Meta:
        db_table = 'veiculos'
        ordering = ['-criado_em']

class Category(models.Model):
    nome = models.CharField(max_length=100)  # Nome da categoria (obrigatório)
    descricao = models.TextField(blank=True, null=True)  # Descrição opcional
    criado_em = models.DateTimeField(auto_now_add=True)  # Data de criação automática

    def __str__(self):
        return self.nome  # Representação legível da categoria no admin e interfaces

    class Meta:
        db_table = 'categorias'  # Nome da tabela no banco
        ordering = ['nome']  # Ordena por nome ao consultar


class Service(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    duracao = models.DurationField()  # Exemplo: timedelta(hours=1, minutes=30)
    categoria = models.ForeignKey(
        'Category',  # ou 'agendamecanica.Category' se estiver em outro app
        on_delete=models.RESTRICT,
        related_name='servicos'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.categoria.nome})"

    class Meta:
        db_table = 'servicos'
        ordering = ['nome']


class Mechanic(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mechanic'
    )
    specialties = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list,
        help_text="Especialidades do mecânico, ex: freios, suspensão"
    )
    available_hours = JSONField(default=dict)  # Exemplo: {"segunda": ["08:00-17:00"]}

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} (Mecânico)"

    class Meta:
        db_table = 'mecanicos'
        ordering = ['-criado_em']


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('em_analise', 'Em análise'),
        ('pendente', 'Pendente'),
        ('concluido', 'Concluído'),
    ]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    mechanic = models.ForeignKey(
        'Mechanic',  # Referência para o modelo Mechanic
        on_delete=models.RESTRICT,
        related_name='appointments'
    )
    service = models.ForeignKey(
        'Service',  # Referência para o modelo Service
        on_delete=models.RESTRICT,
        related_name='appointments'
    )
    vehicle = models.ForeignKey(
        'Vehicle',  # Referência para o modelo Vehicle
        on_delete=models.RESTRICT,
        related_name='appointments'
    )
    appointment_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service.nome} - {self.client.get_full_name()} ({self.appointment_datetime})"

    class Meta:
        db_table = 'agendamentos'
        unique_together = ('mechanic', 'appointment_datetime')  # Evita sobreposição de horários para o mesmo mecânico


class Budget(models.Model):
    STATUS_CHOICES = [
        ('enviado', 'Enviado'),
        ('aprovado', 'Aprovado'),
        ('recusado', 'Recusado'),
    ]

    appointment = models.OneToOneField(
        'Appointment',
        on_delete=models.CASCADE,
        related_name='budget',
        help_text="Agendamento relacionado ao orçamento"
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        help_text="Descrição geral do orçamento ou observações do mecânico"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Valor total do orçamento"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='enviado',
        help_text="Status atual do orçamento"
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Orçamento para {self.appointment}"

    class Meta:
        db_table = 'orcamentos'
        ordering = ['-criado_em']


class BudgetItem(models.Model):
    budget = models.ForeignKey(
        'Budget',
        on_delete=models.CASCADE,
        related_name='itens'
    )
    servico = models.ForeignKey(
        'Service',
        on_delete=models.RESTRICT,
        related_name='budget_items'
    )
    preco_personalizado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f"{self.servico.nome} - R$ {self.preco_personalizado}"

    class Meta:
        db_table = 'itens_orcamento'

class ServiceHistory(models.Model):
    appointment = models.OneToOneField(
        'Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_history',
        help_text='Agendamento original do serviço, se houver.'
    )
    vehicle = models.ForeignKey(
        'Vehicle',
        on_delete=models.CASCADE,
        related_name='historico_servicos'
    )
    mechanic = models.ForeignKey(
        'Mechanic',
        on_delete=models.SET_NULL,
        null=True,
        related_name='servicos_realizados'
    )
    service = models.ForeignKey(
        'Service',
        on_delete=models.SET_NULL,
        null=True,
        related_name='historicos'
    )
    data_realizacao = models.DateField(auto_now_add=True)
    valor_cobrado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.vehicle.placa} - {self.service.nome} em {self.data_realizacao}"

    class Meta:
        db_table = 'historico_servicos'
        ordering = ['-data_realizacao']
 
