# utils.py
from datetime import datetime, timedelta
from .models import Appointment

def gerar_horarios_disponiveis(mecanico):
    hoje = datetime.now().date()
    horarios_livres = []

    dias_traduzidos = {
        'monday': 'segunda',
        'tuesday': 'terca',
        'wednesday': 'quarta',
        'thursday': 'quinta',
        'friday': 'sexta',
        'saturday': 'sabado',
        'sunday': 'domingo'
    }

    for i in range(7):  # próximos 7 dias
        dia = hoje + timedelta(days=i)
        nome_dia = dias_traduzidos.get(dia.strftime('%A').lower())

        if not nome_dia or nome_dia not in mecanico.available_hours:
            continue

        for intervalo in mecanico.available_hours[nome_dia]:
            inicio_str, fim_str = intervalo.split('-')
            inicio = datetime.combine(dia, datetime.strptime(inicio_str, "%H:%M").time())
            fim = datetime.combine(dia, datetime.strptime(fim_str, "%H:%M").time())

            atual = inicio
            while atual + timedelta(minutes=30) <= fim:
                atual = atual.replace(second=0, microsecond=0)
                if not Appointment.objects.filter(
                    mechanic=mecanico,
                    appointment_datetime=atual
                ).exists():
                    horarios_livres.append(atual.strftime('%d/%m/%Y %H:%M'))
                atual += timedelta(minutes=30)

    return horarios_livres