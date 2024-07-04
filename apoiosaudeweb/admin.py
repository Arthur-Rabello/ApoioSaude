from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Familiar, Paciente

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'email_verified', 'verification_token')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('User Type', {'fields': ('user_type',)}),
    )
    list_display = ('username', 'email', 'email_verified', 'is_staff', 'is_active',)
    list_filter = ('email_verified', 'is_staff', 'is_active',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Familiar)
admin.site.register(Paciente)
