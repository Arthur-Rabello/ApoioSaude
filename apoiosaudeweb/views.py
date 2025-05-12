from django.shortcuts import redirect, render, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, get_user_model
from django.core.exceptions import PermissionDenied
from .utils import formatar_data_pt_br,formatar_data_nascimento_pt_br
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .mixins import FamiliarRequiredMixin, CuidadorFamiliarRequiredMixin, AdminRequiredMixin, AllRequiredMixin, MedicoRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Paciente, Familiar, Medico, Medicamento, NotaObservacao, Consulta, CustomUser, Autorizacao
from .forms import ConsultaForm, ConsultaForm, PacienteForm, CustomUserCreationForm, FamiliarRegisterForm, MedicoRegisterForm, MedicamentoForm


User = get_user_model()

def register(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        familiar_form = FamiliarRegisterForm(request.POST)
        medico_form = MedicoRegisterForm(request.POST)

        if user_form.is_valid():
            user = user_form.save(commit=False)
            user_type = user_form.cleaned_data.get('user_type')

            if user_type == 'familiar':
                if familiar_form.is_valid():
                    user.user_type = user_type
                    user.save()
                    familiar_profile = familiar_form.save(commit=False)
                    familiar_profile.user = user
                    familiar_profile.save()
                    send_verification_email(user, request)
                    messages.success(request, 'Conta criada com sucesso. Verifique seu e-mail.')
                    return redirect('login')
            elif user_type == 'medico':
                if medico_form.is_valid():
                    user.user_type = user_type
                    user.save()
                    medico_profile = medico_form.save(commit=False)
                    medico_profile.user = user
                    medico_profile.save()
                    send_verification_email(user, request)
                    messages.success(request, 'Conta criada com sucesso. Verifique seu e-mail.')
                    return redirect('login')
            elif user_type == 'cuidador':
                user.user_type = user_type
                user.save()
                send_verification_email(user, request)
                messages.success(request, 'Conta criada com sucesso. Verifique seu e-mail.')
                return redirect('login')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        user_form = CustomUserCreationForm()
        familiar_form = FamiliarRegisterForm()
        medico_form = MedicoRegisterForm()

    return render(request, 'registration/register.html', {
        'user_form': user_form,
        'familiar_form': familiar_form,
        'medico_form': medico_form,
    })


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.email_verified:
                messages.error(request, 'Por favor, verifique seu e-mail antes de fazer login.', extra_tags='email_verification')
                return redirect('login')
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'registration/login.html')

@login_required
def index(request):
    user_type = request.user.user_type
    is_familiar_admin = getattr(request.user, 'is_familiar_admin', False)

    # Inicializar o conjunto de pacientes
    pacientes = Paciente.objects.none()

    # Obter pacientes criados pelo usuário se ele for 'familiar' ou 'cuidador'
    if user_type in ['familiar', 'cuidador']:
        pacientes = Paciente.objects.filter(familiares_cuidadores__user=request.user)

    # Obter pacientes autorizados para todos os tipos de usuário
    autorizacoes = Autorizacao.objects.filter(email=request.user.email, autorizado=True)
    pacientes_autorizados = Paciente.objects.filter(id__in=[autorizacao.paciente.id for autorizacao in autorizacoes])

    # Combinar ambos os conjuntos de pacientes
    pacientes = pacientes | pacientes_autorizados

    pacientes_data = []

    for paciente in pacientes.distinct():
        consultas = Consulta.objects.filter(paciente=paciente)
        medicamentos = Medicamento.objects.filter(paciente=paciente)
        notas = NotaObservacao.objects.filter(paciente=paciente)

        pacientes_data.append({
            'paciente': paciente,
            'consultas': consultas,
            'medicamentos': medicamentos,
            'notas': notas,
        })

    context = {
        'pacientes_data': pacientes_data,
        'user_type': user_type,
        'is_familiar_admin': is_familiar_admin,
    }
    return render(request, 'index.html', context)


@login_required
def perfil_generico(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if request.user != user:
        raise PermissionDenied

    profile = None
    user_type = None

    if user.user_type == 'familiar':
        try:
            profile = Familiar.objects.get(user=user)
            user_type = 'familiar'
        except Familiar.DoesNotExist:
            profile = None
    elif user.user_type == 'medico':
        try:
            profile = Medico.objects.get(user=user)
            user_type = 'medico'
        except Medico.DoesNotExist:
            profile = None
    elif user.user_type == 'cuidador':
        try:
            profile = Familiar.objects.get(user=user)
            user_type = 'cuidador'
        except Familiar.DoesNotExist:
            profile = None
    else:
        profile = None

    context = {
        'user': user,
        'profile': profile,
        'user_type': user_type,
    }

    return render(request, 'perfil/perfil_generico.html', context)

def error_404_view(request, exception):
    return render(request, 'errors/404.html', status=404)

def error_500_view(request):
    return render(request, 'errors/500.html', status=500)

def logout_view(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso. Até logo!')
    return redirect('login')

class PacienteListView(LoginRequiredMixin, AllRequiredMixin, ListView):
    model = Paciente
    template_name = 'pacientes/paciente_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.user_type in ['familiar', 'cuidador']:
            pacientes = Paciente.objects.filter(familiares_cuidadores__user=user)
        else:
            # Obtém os pacientes que foram autorizados para este usuário
            autorizacoes = Autorizacao.objects.filter(email=user.email, autorizado=True)
            pacientes = Paciente.objects.filter(id__in=[autorizacao.paciente.id for autorizacao in autorizacoes])

        return pacientes.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pacientes = context['object_list']
        for paciente in pacientes:
            paciente.data_formatada = formatar_data_nascimento_pt_br(paciente.data_nascimento)
        return context


class PacienteDetailView(LoginRequiredMixin, AllRequiredMixin, DetailView):
    model = Paciente
    template_name = 'pacientes/paciente_detail.html'

    def get_object(self, queryset=None):
        # Pega o objeto do paciente
        
        paciente = super().get_object(queryset)
        user = self.request.user
        
        # Verificar se o usuário tem permissão para acessar este paciente
        if not Autorizacao.objects.filter(email=user.email, paciente=paciente, autorizado=True).exists():
            raise PermissionDenied("Você não tem permissão para acessar este paciente.")
        
        # Retorna o paciente encontrado
        return paciente

    def get_context_data(self, **kwargs):
        # Pega o contexto padrão da DetailView
        context = super().get_context_data(**kwargs)
        
        # Adiciona o paciente ao contexto
        context['paciente'] = self.get_object()
        
        return context

@login_required
def create_paciente(request):
    if request.user.user_type != 'medico': 
        if request.method == 'POST':
            form = PacienteForm(request.POST, request.FILES)
            if form.is_valid():
               
                paciente = form.save()

                user_role = request.user.user_type

                autorizacao, created = Autorizacao.objects.get_or_create(
                    email=request.user.email,  
                    paciente=paciente,         
                    autorizado=True            
                )

                if user_role == 'familiar':
                    familiar = Familiar.objects.get(user=request.user)
                    familiar.is_admin = True 
                    familiar.relacao_com_paciente = request.POST.get('relacao_com_paciente')
                    familiar.pacientes.add(paciente)
                    familiar.save()
                elif user_role == 'cuidador':
                    familiar = Familiar.objects.get(user=request.user)
                    familiar.is_admin = True  
                    familiar.relacao_com_paciente = request.user.user_type
                    familiar.pacientes.add(paciente)
                    familiar.save()

                messages.success(request, 'Paciente criado com sucesso!')
                return redirect('index')  

        else:
            form = PacienteForm()
    else:
        raise PermissionDenied  

    return render(request, 'pacientes/paciente_form.html', {'form': form})


@login_required
def assign_role(request):
    if not request.user.is_familiar_admin:
        return redirect('index')  
    
    if request.method == 'POST':
        email = request.POST.get('email')
        paciente_id = request.POST.get('paciente_id')
        autorizado = request.POST.get('autorizado') == 'on'
        
        paciente = get_object_or_404(Paciente, id=paciente_id)
        autorizacao, created = Autorizacao.objects.get_or_create(email=email, paciente=paciente)
        autorizacao.autorizado = autorizado
        autorizacao.save()

        return redirect('assign_role')
    
    pacientes = Paciente.objects.all()
    context = {
        'pacientes': pacientes,
    }
    return render(request, 'common/assign_role.html', context)


class PacienteUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'pacientes/paciente_form.html'
    success_url = reverse_lazy('paciente_list')

class PacienteDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Paciente
    template_name = 'pacientes/paciente_confirm_delete.html'
    success_url = reverse_lazy('paciente_list')


class FamiliarDetailView(LoginRequiredMixin, AllRequiredMixin, DetailView):
    model = Familiar
    template_name = 'familiares/familiar_detail.html' 

class FamiliarUpdateView(LoginRequiredMixin, FamiliarRequiredMixin, UpdateView):
    model = Familiar
    fields = ['nome', 'relacao_com_paciente', 'informacoes_contato']
    template_name = 'familiares/familiar_form.html'  
    success_url = reverse_lazy('familiar_list')

class FamiliarDeleteView(LoginRequiredMixin, FamiliarRequiredMixin, DeleteView):
    model = Familiar
    template_name = 'familiares/familiar_confirm_delete.html'  
    success_url = reverse_lazy('familiar_list')

@login_required
def autorizado_list_view(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    user_type = request.user.user_type

    autorizacoes = Autorizacao.objects.filter(paciente=paciente, autorizado=True)
    autorizados_emails = autorizacoes.values_list('email', flat=True)

    medicos_autorizados = Medico.objects.filter(user__email__in=autorizados_emails)
    familiares_autorizados = Familiar.objects.filter(user__email__in=autorizados_emails)

    context = {
        'paciente': paciente,
        'medicos_autorizados': medicos_autorizados,
        'familiares_autorizados': familiares_autorizados,
        'user_type': user_type,
    }
    
    return render(request, 'common/autoridade_list.html', context)

class MedicoDetailView(LoginRequiredMixin, AllRequiredMixin, DetailView):
    model = Medico
    template_name = 'medicos/medico_detail.html'  

class MedicoUpdateView(LoginRequiredMixin,MedicoRequiredMixin, UpdateView):
    model = Medico
    fields = ['nome', 'especialidade', 'informacoes_contato']
    template_name = 'medicos/medico_form.html'  
    success_url = reverse_lazy('medico_list')

class MedicoDeleteView(LoginRequiredMixin,MedicoRequiredMixin,DeleteView):
    model = Medico
    template_name = 'medicos/medico_confirm_delete.html'  
    success_url = reverse_lazy('medico_list')

class MedicamentoListView(LoginRequiredMixin, AllRequiredMixin, ListView):
    model = Medicamento
    template_name = 'medicamentos/medicamento_list.html'
    context_object_name = 'medicamentos_autorizados'

    def get_queryset(self):
        user = self.request.user
        user_type = user.user_type
        pacientes = Paciente.objects.none()

        if user_type in ['familiar', 'cuidador']:
            pacientes = Paciente.objects.filter(familiares_cuidadores__user=user)

        autorizacoes = Autorizacao.objects.filter(email=user.email, autorizado=True)
        pacientes_autorizados_ids = autorizacoes.values_list('paciente_id', flat=True)
        pacientes_autorizados = Paciente.objects.filter(id__in=pacientes_autorizados_ids)

        pacientes = pacientes | pacientes_autorizados

        return Medicamento.objects.filter(paciente__in=pacientes.distinct())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = self.request.user.user_type
        context['is_familiar_admin'] = getattr(self.request.user, 'is_familiar_admin', False)
        return context 

class MedicamentoDetailView(LoginRequiredMixin, CuidadorFamiliarRequiredMixin, DetailView):
    model = Medicamento
    template_name = 'medicamentos/medicamento_detail.html'

    def get_object(self, queryset=None):
        medicamento = super().get_object(queryset)
        return medicamento


class MedicamentoCreateView(LoginRequiredMixin, CuidadorFamiliarRequiredMixin, CreateView):
    model = Medicamento
    form_class = MedicamentoForm
    template_name = 'medicamentos/medicamento_form.html'
    success_url = reverse_lazy('medicamento_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        user = self.request.user
       
        pacientes = Paciente.objects.filter(familiares_cuidadores__user=user)
     
        autorizacoes = Autorizacao.objects.filter(email=user.email, autorizado=True)
        pacientes_autorizados = Paciente.objects.filter(id__in=[autorizacao.paciente.id for autorizacao in autorizacoes])

        pacientes = pacientes | pacientes_autorizados

        form.fields['paciente'].queryset = pacientes.distinct()

        return form

    def form_valid(self, form):
        form.instance.autor = self.request.user
        return super().form_valid(form)

class MedicamentoUpdateView(LoginRequiredMixin, CuidadorFamiliarRequiredMixin, UpdateView):
    model = Medicamento
    form_class = MedicamentoForm
    template_name = 'medicamentos/medicamento_form.html'
    success_url = reverse_lazy('medicamento_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user

        pacientes = Paciente.objects.filter(familiares_cuidadores__user=user)

        autorizacoes = Autorizacao.objects.filter(email=user.email, autorizado=True)
        pacientes_autorizados = Paciente.objects.filter(id__in=[autorizacao.paciente.id for autorizacao in autorizacoes])

        pacientes = pacientes | pacientes_autorizados

        form.fields['paciente'].queryset = pacientes.distinct()

        paciente_atual = self.get_object().paciente
        if paciente_atual not in pacientes:
            raise PermissionDenied("Você não tem permissão para editar este medicamento para o paciente selecionado.")

        return form

    def form_valid(self, form):
        form.instance.autor = self.request.user
        return super().form_valid(form)


class MedicamentoDeleteView(LoginRequiredMixin, CuidadorFamiliarRequiredMixin,DeleteView):
    model = Medicamento
    template_name = 'medicamentos/medicamento_confirm_delete.html'  
    success_url = reverse_lazy('medicamento_list')


class NotaObservacaoListView(LoginRequiredMixin, CuidadorFamiliarRequiredMixin,ListView):
    model = NotaObservacao
    template_name = 'notas/nota_list.html'
    context_object_name = 'notas_autorizadas'

    def get_queryset(self):
        user = self.request.user
        user_type = user.user_type
        pacientes = Paciente.objects.none()

        if user_type in ['familiar', 'cuidador']:
            pacientes = Paciente.objects.filter(familiares_cuidadores__user=user)

        autorizacoes = Autorizacao.objects.filter(email=user.email, autorizado=True)
        pacientes_autorizados_ids = autorizacoes.values_list('paciente_id', flat=True)
        pacientes_autorizados = Paciente.objects.filter(id__in=pacientes_autorizados_ids)

        pacientes = pacientes | pacientes_autorizados

        notas = NotaObservacao.objects.filter(paciente__in=pacientes.distinct())
        for nota in notas:
            nota.data_formatada = nota.data_hora.strftime('%d/%m - %H:%M')
        return notas

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = self.request.user.user_type
        context['is_familiar_admin'] = getattr(self.request.user, 'is_familiar_admin', False)
        return context
class NotaObservacaoDetailView(LoginRequiredMixin, CuidadorFamiliarRequiredMixin, DetailView):
    model = NotaObservacao
    template_name = 'notas/nota_detail.html'

    def get_object(self, queryset=None):
        nota = super().get_object(queryset)
    

        return nota


class NotaObservacaoCreateView(LoginRequiredMixin, CuidadorFamiliarRequiredMixin, CreateView):
    model = NotaObservacao
    fields = ['conteudo', 'paciente']
    template_name = 'notas/nota_form.html'  
    success_url = reverse_lazy('nota_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        user = self.request.user

        pacientes = Paciente.objects.filter(familiares_cuidadores__user=user)

        autorizacoes = Autorizacao.objects.filter(email=user.email, autorizado=True)
        pacientes_autorizados = Paciente.objects.filter(id__in=[autorizacao.paciente.id for autorizacao in autorizacoes])

        pacientes = pacientes | pacientes_autorizados

        form.fields['paciente'].queryset = pacientes.distinct()

        return form

    def form_valid(self, form):

        form.instance.autor = self.request.user
        return super().form_valid(form)
class NotaObservacaoUpdateView(LoginRequiredMixin, CuidadorFamiliarRequiredMixin, UpdateView):
    model = NotaObservacao
    fields = ['conteudo', 'paciente']
    template_name = 'notas/nota_form.html'
    success_url = reverse_lazy('nota_list')

    def get_form(self, form_class=None):

        form = super().get_form(form_class)
        user = self.request.user
    
        pacientes = Paciente.objects.filter(familiares_cuidadores__user=user)
        
        autorizacoes = Autorizacao.objects.filter(email=user.email, autorizado=True)
        pacientes_autorizados = Paciente.objects.filter(id__in=[autorizacao.paciente.id for autorizacao in autorizacoes])

        pacientes = pacientes | pacientes_autorizados

        form.fields['paciente'].queryset = pacientes.distinct()

        paciente_atual = self.get_object().paciente
        if paciente_atual not in pacientes:
            raise PermissionDenied("Você não tem permissão para editar a nota deste paciente.")

        return form

    def form_valid(self, form):
        return super().form_valid(form)


class NotaObservacaoDeleteView(LoginRequiredMixin, CuidadorFamiliarRequiredMixin ,DeleteView):
    model = NotaObservacao
    template_name = 'notas/nota_confirm_delete.html'  
    success_url = reverse_lazy('nota_list')


class ConsultaListView(LoginRequiredMixin, CuidadorFamiliarRequiredMixin ,ListView):
    model = Consulta
    template_name = 'consultas/consulta_list.html'
    context_object_name = 'consultas_autorizadas'

    def get_queryset(self):
        user = self.request.user
        user_type = user.user_type
        pacientes = Paciente.objects.none()

        if user_type in ['familiar', 'cuidador']:
            pacientes = Paciente.objects.filter(familiares_cuidadores__user=user)

        autorizacoes = Autorizacao.objects.filter(email=user.email, autorizado=True)
        pacientes_autorizados_ids = autorizacoes.values_list('paciente_id', flat=True)
        pacientes_autorizados = Paciente.objects.filter(id__in=pacientes_autorizados_ids)

        pacientes = pacientes | pacientes_autorizados

        return Consulta.objects.filter(paciente__in=pacientes.distinct())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = self.request.user.user_type
        context['is_familiar_admin'] = getattr(self.request.user, 'is_familiar_admin', False)
        return context

class ConsultaDetailView(LoginRequiredMixin, CuidadorFamiliarRequiredMixin, DetailView):
    model = Consulta
    template_name = 'consultas/consulta_detail.html'

    def get_object(self, queryset=None):
        consulta = super().get_object(queryset)
        return consulta

class ConsultaCreateView(LoginRequiredMixin, CuidadorFamiliarRequiredMixin, CreateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = 'consultas/consulta_form.html'
    success_url = reverse_lazy('consulta_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user

        # Filtra pacientes associados ao usuário (familiares e cuidadores)
        pacientes = Paciente.objects.filter(familiares_cuidadores__user=user)

        # Filtra pacientes autorizados para o usuário
        autorizacoes = Autorizacao.objects.filter(email=user.email, autorizado=True)
        pacientes_autorizados = Paciente.objects.filter(id__in=[autorizacao.paciente.id for autorizacao in autorizacoes])

        # Combina os dois conjuntos de pacientes
        pacientes = pacientes | pacientes_autorizados

        # Define o queryset do campo 'paciente' para mostrar apenas os pacientes autorizados
        form.fields['paciente'].queryset = pacientes.distinct()

        return form

    def form_valid(self, form):
        # Associa o médico (usuário logado) ao campo 'medico'
     
        
        return super().form_valid(form)

class ConsultaUpdateView(LoginRequiredMixin, CuidadorFamiliarRequiredMixin, UpdateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = 'consultas/consulta_form.html'
    success_url = reverse_lazy('consulta_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user

        # Filtra pacientes associados ao usuário (familiares e cuidadores)
        pacientes = Paciente.objects.filter(familiares_cuidadores__user=user)

        # Filtra pacientes autorizados para o usuário
        autorizacoes = Autorizacao.objects.filter(email=user.email, autorizado=True)
        pacientes_autorizados = Paciente.objects.filter(id__in=[autorizacao.paciente.id for autorizacao in autorizacoes])

        # Combina os dois conjuntos de pacientes
        pacientes = pacientes | pacientes_autorizados

        # Define o queryset do campo 'paciente' para mostrar apenas os pacientes autorizados
        form.fields['paciente'].queryset = pacientes.distinct()

        # Verifica se o paciente associado à consulta ainda é autorizado para o usuário
        paciente_atual = self.get_object().paciente
        if paciente_atual not in pacientes:
            # Se o paciente não estiver na lista de pacientes autorizados, lança um erro
            raise PermissionDenied("Você não tem permissão para editar esta consulta para o paciente selecionado.")

        return form

    def form_valid(self, form):
        form.instance.autor = self.request.user
        return super().form_valid(form)


class ConsultaDeleteView(LoginRequiredMixin, CuidadorFamiliarRequiredMixin ,DeleteView):
    model = Consulta
    template_name = 'consultas/consulta_confirm_delete.html'
    success_url = reverse_lazy('consulta_list')

def permission_denied_view(request, exception):
    return render(request, 'permission_denied.html', status=403)

@login_required
def delete_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    # Apenas o próprio usuário pode deletar o perfil
    if request.user == user:
        user.delete()
        messages.success(request, 'Perfil deletado com sucesso.')
        return redirect('index')
    else:
        messages.error(request, 'Você não tem permissão para deletar este perfil.')
        return redirect('perfil/perfil_generico', user_id=user_id)


@login_required
def autorizacao_acesso(request, paciente_id):
    if not hasattr(request.user, 'familiar') or not request.user.familiar.is_admin:
        raise PermissionDenied

    paciente = get_object_or_404(Paciente, id=paciente_id)
    autorizacoes = Autorizacao.objects.filter(paciente=paciente).select_related('paciente')
    autorizados_info = []

    for autorizacao in autorizacoes:
        user = get_object_or_404(CustomUser, email=autorizacao.email)
        relacao_com_paciente = ''
        if user.user_type == 'familiar':
            relacao_com_paciente = Familiar.objects.get(user=user).relacao_com_paciente
        autorizados_info.append({
            'nome_usuario': user.username,
            'email': autorizacao.email,
            'paciente': autorizacao.paciente,
            'relacao_com_paciente': relacao_com_paciente if relacao_com_paciente else user.get_user_type_display(),
            'id': autorizacao.id  # Adiciona o ID da autorização para remoção
        })

    if request.method == 'POST':
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')
        autorizado = request.POST.get('autorizado') == 'on'
        relacao_com_paciente = request.POST.get('relacao_com_paciente')

        user = get_object_or_404(CustomUser, email=email)
        if user.user_type == 'familiar' and not relacao_com_paciente:
            messages.error(request, 'O campo "Relação com o Paciente" é obrigatório.')
            context = {
                'paciente': paciente,
                'autorizados_info': autorizados_info,
            }
            return render(request, 'common/autorizacao_acesso.html', context)

        autorizacao, created = Autorizacao.objects.get_or_create(email=email, paciente=paciente)
        autorizacao.autorizado = autorizado
        autorizacao.save()

        if user.user_type == 'familiar' and relacao_com_paciente:
            familiar = Familiar.objects.get(user=user)
            familiar.relacao_com_paciente = relacao_com_paciente
            familiar.save()

        messages.success(request, 'Autorização atualizada com sucesso.')
        autorizacoes = Autorizacao.objects.filter(paciente=paciente).select_related('paciente')
        autorizados_info = []
        for autorizacao in autorizacoes:
            user = get_object_or_404(CustomUser, email=autorizacao.email)
            relacao_com_paciente = ''
            if user.user_type == 'familiar':
                relacao_com_paciente = Familiar.objects.get(user=user).relacao_com_paciente
            autorizados_info.append({
                'nome_usuario': user.username,
                'email': autorizacao.email,
                'paciente': autorizacao.paciente,
                'relacao_com_paciente': relacao_com_paciente if relacao_com_paciente else user.get_user_type_display(),
                'id': autorizacao.id
            })
        
        context = {
            'paciente': paciente,
            'autorizados_info': autorizados_info,
        }
        return render(request, 'common/autorizacao_acesso.html', context)

    context = {
        'paciente': paciente,
        'autorizados_info': autorizados_info,
    }
    return render(request, 'common/autorizacao_acesso.html', context)


@login_required
def remover_autorizacao(request, autorizacao_id):
    autorizacao = get_object_or_404(Autorizacao, id=autorizacao_id)
    paciente_id = autorizacao.paciente.id
    autorizacao.delete()
    
    return redirect('autorizacao_acesso', paciente_id)

@login_required
def editar_perfil(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    
    if user.user_type == 'familiar' or user.user_type == 'cuidador':
        profile = get_object_or_404(Familiar, user=user)
        form_class = FamiliarRegisterForm
    elif user.user_type == 'medico':
        profile = get_object_or_404(Medico, user=user)
        form_class = MedicoRegisterForm
    else:
        messages.error(request, 'Tipo de usuário inválido.')
        return redirect('perfil_generico', user_id=user.id)
    
    if request.method == 'POST':
        form = form_class(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso.')
            return redirect('perfil_generico', user_id=user.id)
    else:
        form = form_class(instance=profile)
    
    return render(request, 'perfil/editar_perfil.html', {'form': form, 'user': user})

def verify_email(request, token):
    user = get_object_or_404(CustomUser, verification_token=token)
    user.email_verified = True
    user.is_active = True
    user.save()
    messages.success(request, 'E-mail verificado com sucesso!')
    return redirect('login')

def trigger_error(request):
    # Aqui provocamos uma exceção dividindo por zero
    return 1 / 0



def send_verification_email(user, request):
    subject = 'Verifique seu e-mail'
    token = str(user.verification_token)
    verification_link = request.build_absolute_uri(reverse('verify_email', kwargs={'token': token}))
    message = f'Clique no link para verificar seu e-mail: {verification_link}'
    from_email = 'Verifique seu e-mail <jucax30@gmail.com>'
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)

def resend_verification_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            if not user.email_verified:
                send_verification_email(user, request)
                messages.success(request, 'E-mail de verificação reenviado com sucesso.')
            else:
                messages.info(request, 'Seu e-mail já está verificado.')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
        return redirect('login')
    return render(request, 'registration/resend_verification_email.html')
