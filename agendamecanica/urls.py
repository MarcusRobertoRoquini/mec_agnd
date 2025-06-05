from django.urls import path
from . import views

urlpatterns = [
    # Cadastro e login
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('register/mecanico/', views.cadastro_mecanico, name='cadastro_mecanico'),

    # Home pages
    path('clientehome/', views.cliente_home, name='cliente_home'),
    path('mecanicohome/', views.mecanico_home, name='mecanico_home'),

    # Veículos
    path('veiculo/novo/', views.adicionar_veiculo, name='adicionar_veiculo'),
    path('veiculo/<int:pk>/editar/', views.editar_veiculo, name='editar_veiculo'),

    # Agendamento
    path('iniciar_agendamento/', views.iniciar_agendamento_view, name='iniciar_agendamento'),
    path('selecionar_mecanico/<int:veiculo_id>/<int:categoria_id>/<int:servico_id>/', views.selecionar_mecanico, name='selecionar_mecanico'),
    path('ajax/horarios-disponiveis/<int:mecanico_id>/', views.horarios_disponiveis, name='horarios_disponiveis'),
    path('ajax/servicos-por-categoria/<int:categoria_id>/', views.servicos_por_categoria, name='servicos_por_categoria'),
    path('confirmar-agendamento/', views.confirmar_agendamento, name='confirmar_agendamento'),

    # Novas rotas:
    path('atualizar-status/<int:agendamento_id>/<str:novo_status>/', views.atualizar_status, name='atualizar_status'),
    path('mecanico/orcamento/<int:appointment_id>/criar/', views.criar_orcamento, name='criar_orcamento'),
    path('ver_orcamento/<int:appointment_id>/', views.ver_orcamento, name='ver_orcamento'),


]

