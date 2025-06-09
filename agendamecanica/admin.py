from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Vehicle, Category, Service, Mechanic, Appointment, Budget, BudgetItem, ServiceHistory, Cliente, RelatorioDummy
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import admin
from django.shortcuts import redirect

# --- Custom User ---
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'telefone', 'aprovado')}),
    )
    list_display = ('username', 'email', 'role', 'aprovado')
    list_filter = ('role', 'aprovado')

admin.site.register(User, CustomUserAdmin)

# --- Mechanic Admin ---
@admin.register(Mechanic)
class MechanicAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_approved', 'display_specialties', 'criado_em')
    list_filter = ('is_approved', 'specialties', 'criado_em')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    actions = ['aprovar_mecanicos', 'reprovar_mecanicos']

    @admin.action(description="Aprovar mecânicos selecionados")
    def aprovar_mecanicos(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} mecânico(s) aprovado(s).")

    @admin.action(description="Reprovar mecânicos selecionados")
    def reprovar_mecanicos(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} mecânico(s) reprovado(s).")

    @admin.display(description="Especialidades")
    def display_specialties(self, obj):
        return ", ".join([c.nome for c in obj.specialties.all()])

# --- Budget Inline ---
class BudgetInline(admin.StackedInline):
    model = Budget
    extra = 0
    show_change_link = True
    readonly_fields = ('status', 'criado_em')


# --- Appointment Admin ---
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'client_name', 'mechanic_name',
        'appointment_date', 'appointment_time',
        'status', 'vehicle_info'
    )
    list_filter = ('status', 'appointment_datetime', 'mechanic')
    search_fields = (
        'client__first_name', 'client__last_name',
        'mechanic__user__first_name', 'mechanic__user__last_name',
        'vehicle__modelo'
    )
    actions = [admin.action(description="Marcar como concluído")(lambda modeladmin, request, queryset: queryset.update(status='concluido'))]
    inlines = [BudgetInline]

    def client_name(self, obj):
        return obj.client.get_full_name()
    def mechanic_name(self, obj):
        return obj.mechanic.user.get_full_name()
    def appointment_date(self, obj):
        return obj.appointment_datetime.date()
    def appointment_time(self, obj):
        return obj.appointment_datetime.time()
    def vehicle_info(self, obj):
        return f"{obj.vehicle.marca} {obj.vehicle.modelo}"

    client_name.short_description = 'Cliente'
    mechanic_name.short_description = 'Mecânico'
    appointment_date.short_description = 'Data'
    appointment_time.short_description = 'Hora'
    vehicle_info.short_description = 'Veículo'

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'telefone', 'aprovado', 'contar_veiculos', 'contar_agendamentos')
    list_filter = ('aprovado',)
    search_fields = ('first_name', 'last_name', 'email', 'telefone')
    actions = ['aprovar_clientes', 'suspender_clientes']

    def get_queryset(self, request):
        # Apenas usuários com role = 'cliente'
        return super().get_queryset(request).filter(role='cliente')

    @admin.display(description='Nome completo')
    def full_name(self, obj):
        return obj.get_full_name()

    @admin.display(description='Veículos')
    def contar_veiculos(self, obj):
        return obj.vehicles.count()

    @admin.display(description='Agendamentos')
    def contar_agendamentos(self, obj):
        return obj.appointments.count()

    @admin.action(description="Aprovar clientes selecionados")
    def aprovar_clientes(self, request, queryset):
        updated = queryset.update(aprovado=True)
        self.message_user(request, f"{updated} cliente(s) aprovado(s).")

    @admin.action(description="Suspender clientes selecionados")
    def suspender_clientes(self, request, queryset):
        updated = queryset.update(aprovado=False)
        self.message_user(request, f"{updated} cliente(s) suspenso(s).")


@admin.register(ServiceHistory)
class ServiceHistoryAdmin(admin.ModelAdmin):
    change_list_template = "admin/servico_extra.html"

# opcionalmente, criar um ModelAdmin "dummy"
class RelatorioAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect(reverse('relatorios_admin'))

admin.site.register(Service, RelatorioAdmin)


class RelatorioAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        # Redireciona para a URL personalizada do relatório
        return redirect(reverse('relatorios_admin'))

admin.site.register(RelatorioDummy, RelatorioAdmin)


# --- Outros modelos ---
admin.site.register(Vehicle)
admin.site.register(Category)

admin.site.register(Budget)
admin.site.register(BudgetItem)

