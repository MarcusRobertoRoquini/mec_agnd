from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = (
        ('cliente', 'Cliente'),
        ('mecanico', 'Mecânico'),
        ('admin', 'Administrador'),
    )
    telefone = models.CharField(max_length=20)
    role = models.CharField(max_length=10, choices=ROLES)
    aprovado = models.BooleanField(default=False)  # para aprovação de mecânicos
