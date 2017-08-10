from django.contrib import admin

# Register your models here.
from .models import Batch

class BatchAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'batch_date')
        }),
        ('OMR data', {
            'fields': ('omr_baseline', 'omr_self_aware', 'omr_career_aware',
                       'omr_career_planning', 'comment')
        }),
        ('Transformed data', {
            'classes': ('collapse',),
            'fields': ('proc_baseline', 'proc_self_aware', 'proc_career_aware',
                       'proc_career_planning', 'status'),
        }),
    )


admin.site.register(Batch, BatchAdmin)