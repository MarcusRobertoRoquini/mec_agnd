from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Appointment, ServiceHistory

@receiver(post_save, sender=Appointment)
def criar_historico_servico(sender, instance, created, **kwargs):
    # Verifica se o status foi alterado para "concluido"
    if instance.status == 'concluido':
        # Garante que o histórico ainda não foi criado
        if not hasattr(instance, 'service_history'):
            ServiceHistory.objects.create(
                appointment=instance,
                vehicle=instance.vehicle,
                mechanic=instance.mechanic,
                service=instance.service,
                valor_cobrado=instance.service.preco,
                observacoes=f"Serviço concluído em {instance.appointment_datetime.strftime('%d/%m/%Y')}"
            )
