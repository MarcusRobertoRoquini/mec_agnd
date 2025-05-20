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
admin.site.register(Mechanic)
admin.site.register(Appointment)
admin.site.register(Budget)
admin.site.register(BudgetItem)
admin.site.register(ServiceHistory)