from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('register/mecanico/', views.cadastro_mecanico, name='cadastro_mecanico'),
    path('clientehome/', views.cliente_home, name='cliente_home'),
    path('mecanicohome/', views.mecanico_home, name='mecanico_home'),
]
