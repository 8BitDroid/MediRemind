from django.contrib import admin
from .models import Medicine, DoseLog


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'dosage', 'frequency', 'time_slot_1', 'is_active', 'start_date']
    list_filter = ['is_active', 'frequency', 'meal_instruction']
    search_fields = ['name', 'user__username']
    list_per_page = 20


@admin.register(DoseLog)
class DoseLogAdmin(admin.ModelAdmin):
    list_display = ['medicine', 'user', 'scheduled_date', 'scheduled_time', 'status', 'taken_at']
    list_filter = ['status', 'scheduled_date']
    search_fields = ['medicine__name', 'user__username']
    list_per_page = 20
