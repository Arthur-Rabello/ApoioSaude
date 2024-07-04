from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Consulta, Paciente, Familiar, Medico, CustomUser,NotaObservacao,Autorizacao, Medicamento
from django.utils.translation import gettext_lazy as _

TIPOS_SANGUINEOS = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('O+', 'O+'),
    ('O-', 'O-'),
]

class ConsultaForm(forms.ModelForm):
    data = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    hora = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Consulta
        fields = ['data', 'hora', 'paciente', 'medico', 'descricao']

class PacienteForm(forms.ModelForm):
    tipo_sanguineo = forms.ChoiceField(
        choices=TIPOS_SANGUINEOS,
        widget=forms.Select
    )
    data_nascimento = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date'},
            format='%Y-%m-%d'  # Ajuste o formato aqui conforme o esperado pelo HTML5
        )
    )

    class Meta:
        model = Paciente
        fields = ['nome', 'data_nascimento', 'tipo_sanguineo', 'doenca', 'outros_dados', 'foto_perfil']

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="E-mail")
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES, required=True, label="Tipo de usuário")
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Confirmação de senha",
        widget=forms.PasswordInput
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'user_type']
        labels = {
            'username': 'Nome de usuário',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False 
        if commit:
            user.save()
        return user
        
class FamiliarRegisterForm(forms.ModelForm):
    class Meta:
        model = Familiar
        fields = ['nome', 'informacoes_contato']

class MedicoRegisterForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['nome', 'especialidade', 'informacoes_contato']

class NotaObservacaoForm(forms.ModelForm):
    class Meta:
        model = NotaObservacao
        fields = ['conteudo', 'paciente']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Filtrar os pacientes autorizados para o usuário logado
            autorizacoes = Autorizacao.objects.filter(email=user.email, autorizado=True)
            paciente_ids = autorizacoes.values_list('paciente_id', flat=True)
            self.fields['paciente'].queryset = Paciente.objects.filter(id__in=paciente_ids)

class MedicamentoForm(forms.ModelForm):
    class Meta:
        model = Medicamento
        fields = ['nome', 'dosagem', 'frequencia', 'paciente']