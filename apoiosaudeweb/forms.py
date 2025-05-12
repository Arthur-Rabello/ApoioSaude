from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Consulta, Paciente, Familiar, Medico, CustomUser, NotaObservacao, Autorizacao, Medicamento

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
    data = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Escolha a data da consulta'})
    )
    hora = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'placeholder': 'Escolha a hora da consulta'})
    )

    class Meta:
        model = Consulta
        fields = ['data', 'hora', 'paciente', 'medico', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'placeholder': 'Descreva a consulta ou os motivos da visita'})
        }

class PacienteForm(forms.ModelForm):
    tipo_sanguineo = forms.ChoiceField(
        choices=TIPOS_SANGUINEOS,
        widget=forms.Select(attrs={'placeholder': 'Selecione o tipo sanguíneo'})
    )
    data_nascimento = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'placeholder': 'Digite a data de nascimento'}
        )
    )
    relacao_com_paciente = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Filho, Esposa'})
    )
    
    class Meta:
        model = Paciente
        fields = ['nome', 'data_nascimento', 'tipo_sanguineo', 'relacao_com_paciente', 'doenca', 'outros_dados', 'foto_perfil']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome completo do paciente'}),
            'doenca': forms.Textarea(attrs={'placeholder': 'Informe as doenças ou condições do paciente'}),
            'outros_dados': forms.Textarea(attrs={'placeholder': 'Outras informações relevantes sobre o paciente'}),
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="E-mail", widget=forms.EmailInput(attrs={'placeholder': 'Informe seu e-mail'}))
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES, required=True, label="Tipo de usuário")
    password1 = forms.CharField(
        label="Senha", 
        widget=forms.PasswordInput(attrs={'placeholder': 'Crie uma senha forte'})
    )
    password2 = forms.CharField(
        label="Confirmação de senha", 
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita a senha'})
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
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome completo do familiar'}),
            'informacoes_contato': forms.Textarea(attrs={'placeholder': 'Informações de contato (telefone, e-mail)'}),
        }

class MedicoRegisterForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['nome', 'especialidade', 'informacoes_contato']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome completo do médico'}),
            'especialidade': forms.TextInput(attrs={'placeholder': 'Ex: Cardiologista, Pediatra'}),
            'informacoes_contato': forms.Textarea(attrs={'placeholder': 'Informações de contato do médico (telefone, e-mail)'}),
        }

class NotaObservacaoForm(forms.ModelForm):
    class Meta:
        model = NotaObservacao
        fields = ['conteudo', 'paciente']
    
    def __init__(self, *args, **kwargs):
        super(NotaObservacaoForm, self).__init__(*args, **kwargs)
        
        user = kwargs.get('user')
        if user:
            pacientes = Paciente.objects.filter(familiares_cuidadores__user=user)
            autorizacoes = Autorizacao.objects.filter(email=user.email, autorizado=True)
            pacientes_autorizados = Paciente.objects.filter(id__in=[autorizacao.paciente.id for autorizacao in autorizacoes])
            pacientes = pacientes | pacientes_autorizados

            self.fields['paciente'].queryset = pacientes
            self.fields['conteudo'].widget = forms.Textarea(attrs={'placeholder': 'Escreva a nota ou observação sobre o paciente'})

class MedicamentoForm(forms.ModelForm):
    class Meta:
        model = Medicamento
        fields = ['nome', 'dosagem', 'frequencia', 'paciente']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome do medicamento'}),
            'dosagem': forms.TextInput(attrs={'placeholder': 'Ex: 500mg, 1 comprimido'}),
            'frequencia': forms.TextInput(attrs={'placeholder': 'Ex: 2x ao dia, 3x por semana'}),
        }
