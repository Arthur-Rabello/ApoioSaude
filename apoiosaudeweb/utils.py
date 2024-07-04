from babel.dates import format_datetime
from .models import Paciente, Autorizacao

def get_pacientes_data(user):
    # Inicializar o conjunto de pacientes
    pacientes = Paciente.objects.none()

    # Obter pacientes criados pelo usuário se ele for 'familiar' ou 'cuidador'
    if user.user_type in ['familiar', 'cuidador']:
        pacientes = Paciente.objects.filter(familiares_cuidadores__user=user)

    # Obter pacientes autorizados para todos os tipos de usuário
    autorizacoes = Autorizacao.objects.filter(email=user.email, autorizado=True)
    pacientes_autorizados = Paciente.objects.filter(id__in=[autorizacao.paciente.id for autorizacao in autorizacoes])

    # Combinar ambos os conjuntos de pacientes
    pacientes = pacientes | pacientes_autorizados

    # Retornar apenas os IDs dos pacientes
    return [paciente.id for paciente in pacientes.distinct()]


# Dicionário para mapear os meses em português
MESES_PT_BR = {
    "janeiro": "Janeiro",
    "fevereiro": "Fevereiro",
    "março": "Março",
    "abril": "Abril",
    "maio": "Maio",
    "junho": "Junho",
    "julho": "Julho",
    "agosto": "Agosto",
    "setembro": "Setembro",
    "outubro": "Outubro",
    "novembro": "Novembro",
    "dezembro": "Dezembro"
}

def formatar_data_pt_br(data_hora):
    formatted_date = format_datetime(data_hora, "dd'/'MM - HH:mm", locale='pt_BR')
    for mes_en, mes_pt in MESES_PT_BR.items():
        formatted_date = formatted_date.replace(mes_en, mes_pt)
    return formatted_date

def formatar_data_nascimento_pt_br(data_nascimento):
    formatted_date = format_datetime(data_nascimento, "d 'de' MMMM 'de' yyyy", locale='pt_BR')
    for mes_en, mes_pt in MESES_PT_BR.items():
        formatted_date = formatted_date.replace(mes_en, mes_pt)
    return formatted_date