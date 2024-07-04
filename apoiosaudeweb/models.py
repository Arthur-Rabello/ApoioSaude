from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from datetime import date, datetime

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('familiar', _('Familiar')),
        ('cuidador', _('Cuidador')),
        ('medico', _('Medico')),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    email = models.EmailField(unique=True)
    is_familiar_admin = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return self.username

class Paciente(models.Model):
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField(null=True, blank=True)
    tipo_sanguineo = models.CharField(max_length=10)
    doenca = models.CharField(max_length=200)
    outros_dados = models.TextField()
    foto_perfil = models.ImageField(upload_to='perfil_pics', blank=True, null=True)

    def calcular_idade(self):
        if self.data_nascimento is None:
            return None
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))

    def __str__(self):
        return self.nome

class Familiar(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    relacao_com_paciente = models.CharField(max_length=100, blank=True, null=True)
    informacoes_contato = models.CharField(max_length=200, blank=True, null=True)
    tipo = models.CharField(
        max_length=50,
        choices=[('familiar', 'Familiar'), ('cuidador', 'Cuidador')],
        default='familiar'
    )
    pacientes = models.ManyToManyField('Paciente', related_name='familiares_cuidadores')
    is_admin = models.BooleanField(default=False)
    def __str__(self):
        return self.nome

class Medico(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    especialidade = models.CharField(max_length=100)
    informacoes_contato = models.CharField(max_length=200)
    pacientes = models.ManyToManyField('Paciente', related_name='medicos')

    def __str__(self):
        return self.nome

class Medicamento(models.Model):
    nome = models.CharField(max_length=100)
    dosagem = models.CharField(max_length=50)
    frequencia = models.CharField(max_length=50)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)

class NotaObservacao(models.Model):
    data_hora = models.DateTimeField(auto_now_add=True)
    conteudo = models.TextField()
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    autor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.autor.username}: {self.conteudo[:20]}'

class Consulta(models.Model):
    data = models.DateField(_('data'))
    hora = models.TimeField(_('hora'))
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True, blank=True)
    descricao = models.TextField(default='Descrição não fornecida')

    def __str__(self):
        return f"{self.data} {self.hora} - {self.paciente} com {self.medico}"
    
    def formatted_datetime(self):
        combined_datetime = datetime.combine(self.data, self.hora)
        return combined_datetime.strftime('%Y-%m-%dT%H:%M:%S')

class Autorizacao(models.Model):
    email = models.EmailField(default='default@default.com',null=False)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='autorizacoes')
    autorizado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email} - {self.paciente.nome}"