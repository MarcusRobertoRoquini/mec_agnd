# utils.py
from datetime import datetime, timedelta
from .models import Appointment

def gerar_horarios_disponiveis(mecanico):
    hoje = datetime.now().date()
    eventos = []

    dias_traduzidos = {
        'monday': 'segunda',
        'tuesday': 'terca',
        'wednesday': 'quarta',
        'thursday': 'quinta',
        'friday': 'sexta',
        'saturday': 'sabado',
        'sunday': 'domingo'
    }

    for i in range(7):
        dia = hoje + timedelta(days=i)
        nome_dia = dias_traduzidos.get(dia.strftime('%A').lower())

        if not nome_dia or nome_dia not in mecanico.available_hours:
            continue

        for intervalo in mecanico.available_hours[nome_dia]:
            inicio_str, fim_str = intervalo.split('-')
            # Função auxiliar para converter string de horário
            def parse_horario(horario_str):
                horario_str = horario_str.strip()  # <- ESSENCIAL
                formatos = ["%H:%M", "%H:%M:%S"]
                for fmt in formatos:
                    try:
                        return datetime.strptime(horario_str, fmt).time()
                    except ValueError:
                        continue
                raise ValueError(f"Formato de horário inválido: {horario_str}")


            inicio = datetime.combine(dia, parse_horario(inicio_str))
            fim = datetime.combine(dia, parse_horario(fim_str))


            atual = inicio
            while atual + timedelta(hours=1) <= fim:
                atual = atual.replace(second=0, microsecond=0)
                if not Appointment.objects.filter(
                    mechanic=mecanico,
                    appointment_datetime=atual
                ).exists():
                    eventos.append({
                        "title": "Disponível",
                        "start": atual.isoformat(),
                        "end": (atual + timedelta(hours=1)).isoformat(),
                        "extendedProps": {
                            "horario_formatado": atual.strftime('%d/%m/%Y %H:%M'),
                        }
                    })
                atual += timedelta(hours=1)

    return eventos
