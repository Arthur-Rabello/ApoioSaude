from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500, handler403
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import register,trigger_error, login, perfil_generico, resend_verification_email, verify_email, editar_perfil, error_404_view, autorizado_list_view, error_500_view, logout_view, autorizacao_acesso, delete_profile, permission_denied_view, remover_autorizacao


urlpatterns = [
    path('', views.index, name='index'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout_view, name='logout'),
    path('index/', views.index, name='index'),
    path('trigger-error/', trigger_error, name='trigger_error'),
    path('permission_denied/', permission_denied_view, name='permission_denied'),
    path('assign_role/', views.assign_role, name='assign_role'),
    path('verify/<uuid:token>/', verify_email, name='verify_email'),
    path('resend-verification-email/', resend_verification_email, name='resend_verification_email'),

    path('remover_autorizacao/<int:autorizacao_id>/', remover_autorizacao, name='remover_autorizacao'),
    path('autorizacao_acesso/<int:paciente_id>/', autorizacao_acesso, name='autorizacao_acesso'),
    path('autorizados/<int:paciente_id>/', autorizado_list_view, name='autorizado_list'),

    path('perfil/<int:user_id>/', perfil_generico, name='perfil_generico'),
    path('perfil/editar/<int:user_id>/', editar_perfil, name='editar_perfil'),
    path('delete_profile/<int:user_id>/', delete_profile, name='delete_profile'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('pacientes/', views.PacienteListView.as_view(), name='paciente_list'),
    path('pacientes/<int:pk>/', views.PacienteDetailView.as_view(), name='paciente_detail'),
    path('create_paciente/', views.create_paciente, name='create_paciente'),
    path('pacientes/<int:pk>/update/', views.PacienteUpdateView.as_view(), name='paciente_update'),
    path('pacientes/<int:pk>/delete/', views.PacienteDeleteView.as_view(), name='paciente_delete'),

    path('familiares/<int:pk>/', views.FamiliarDetailView.as_view(), name='familiar_detail'),
    path('familiares/<int:pk>/update/', views.FamiliarUpdateView.as_view(), name='familiar_update'),
    path('familiares/<int:pk>/delete/', views.FamiliarDeleteView.as_view(), name='familiar_delete'),

    path('medicos/<int:pk>/', views.MedicoDetailView.as_view(), name='medico_detail'),
    path('medicos/<int:pk>/update/', views.MedicoUpdateView.as_view(), name='medico_update'),
    path('medicos/<int:pk>/delete/', views.MedicoDeleteView.as_view(), name='medico_delete'),
    
    path('medicamentos/', views.MedicamentoListView.as_view(), name='medicamento_list'),
    path('medicamentos/<int:pk>/', views.MedicamentoDetailView.as_view(), name='medicamento_detail'),
    path('medicamentos/create/', views.MedicamentoCreateView.as_view(), name='medicamento_create'),
    path('medicamentos/<int:pk>/update/', views.MedicamentoUpdateView.as_view(), name='medicamento_update'),
    path('medicamentos/<int:pk>/delete/', views.MedicamentoDeleteView.as_view(), name='medicamento_delete'),
    
    path('notas/', views.NotaObservacaoListView.as_view(), name='nota_list'),
    path('notas/<int:pk>/', views.NotaObservacaoDetailView.as_view(), name='nota_detail'),
    path('notas/create/', views.NotaObservacaoCreateView.as_view(), name='nota_create'),
    path('notas/<int:pk>/update/', views.NotaObservacaoUpdateView.as_view(), name='nota_update'),
    path('notas/<int:pk>/delete/', views.NotaObservacaoDeleteView.as_view(), name='nota_delete'),
    
    path('consultas/', views.ConsultaListView.as_view(), name='consulta_list'),
    path('consultas/<int:pk>/', views.ConsultaDetailView.as_view(), name='consulta_detail'),
    path('consultas/create/', views.ConsultaCreateView.as_view(), name='consulta_create'),
    path('consultas/<int:pk>/update/', views.ConsultaUpdateView.as_view(), name='consulta_update'),
    path('consultas/<int:pk>/delete/', views.ConsultaDeleteView.as_view(), name='consulta_delete'),
]