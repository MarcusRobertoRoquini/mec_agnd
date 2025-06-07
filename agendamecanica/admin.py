from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Vehicle, Category, Service, Mechanic, Appointment, Budget, BudgetItem, ServiceHistory



class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'telefone', 'aprovado')}),
    )
    list_display = ('username', 'email', 'role', 'aprovado')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Vehicle)
admin.site.register(Category)
admin.site.register(Service)
admin.site.register(Appointment)
admin.site.register(Budget)
admin.site.register(BudgetItem)
admin.site.register(ServiceHistory)

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


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_name', 'mechanic_name', 'appointment_date', 'appointment_time', 'status', 'vehicle_info')
    list_filter = ('status', 'appointment_datetime', 'mechanic')
    search_fields = (
        'client__first_name', 'client__last_name',
        'mechanic__user__first_name', 'mechanic__user__last_name',
        'vehicle__modelo'
    )

    def client_name(self, obj):
        return obj.client.get_full_name()
    client_name.short_description = 'Cliente'

    def mechanic_name(self, obj):
        return obj.mechanic.user.get_full_name()
    mechanic_name.short_description = 'Mecânico'

    def appointment_date(self, obj):
        return obj.appointment_datetime.date()
    appointment_date.short_description = 'Data'

    def appointment_time(self, obj):
        return obj.appointment_datetime.time()
    appointment_time.short_description = 'Hora'

    def vehicle_info(self, obj):
        return f"{obj.vehicle.marca} {obj.vehicle.modelo}"
    vehicle_info.short_description = 'Veículo'