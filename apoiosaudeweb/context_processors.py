from .utils import get_pacientes_data

def pacientes_context(request):
    if request.user.is_authenticated:
        return {
            'pacientes_ids': get_pacientes_data(request.user)
        }
    return {}
