from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from .models import Paciente, Familiar, Autorizacao
from django.core.exceptions import PermissionDenied

class FamiliarRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'familiar':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class MedicoRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'medico':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class AllRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'medico' and request.user.user_type != 'cuidador' and request.user.user_type != 'familiar':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class CuidadorFamiliarRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'cuidador' and request.user.user_type != 'familiar':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        paciente = get_object_or_404(Paciente, pk=self.kwargs['pk'])
        user = request.user
        if not user.is_authenticated:
            return redirect(reverse('login'))
        try:
            if user.user_type == 'familiar':
                familiar = Familiar.objects.get(user=user, is_admin=True, pacientes=paciente)
            elif user.user_type == 'cuidador':
                familiar = Familiar.objects.get(user=user, is_admin=True, pacientes=paciente)
            else:
                familiar = None
        except Familiar.DoesNotExist:
            familiar = None
        
        if not familiar:
            raise PermissionDenied  # Assumindo que você tenha uma view para permissões negadas

        return super().dispatch(request, *args, **kwargs)
