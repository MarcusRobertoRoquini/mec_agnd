from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('register/mecanico/', views.cadastro_mecanico, name='cadastro_mecanico'),
    path('clientehome/', views.cliente_home, name='cliente_home'),
    path('mecanicohome/', views.mecanico_home, name='mecanico_home'),
    path('veiculo/novo/', views.adicionar_veiculo, name='adicionar_veiculo'),
    path('veiculo/<int:pk>/editar/', views.editar_veiculo, name='editar_veiculo'),
    

    path('iniciar_agendamento', views.iniciar_agendamento_view, name='iniciar_agendamento'),
    path('selecionar_mecanico/<int:veiculo_id>/<int:categoria_id>/<int:servico_id>/', views.selecionar_mecanico, name='selecionar_mecanico'),
    path('ajax/horarios-disponiveis/<int:mecanico_id>/', views.horarios_disponiveis, name='horarios_disponiveis'),
    path('ajax/servicos-por-categoria/<int:categoria_id>/', views.servicos_por_categoria, name='servicos_por_categoria'),
    path('confirmar-agendamento/', views.confirmar_agendamento, name='confirmar_agendamento'),
]
