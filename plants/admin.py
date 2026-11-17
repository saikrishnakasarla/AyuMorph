"""
Admin configuration for the Plants application.
"""

from django.contrib import admin
from .models import Plant

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('name', 'scientific_name', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'scientific_name', 'description', 'identification_features')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Botanical Taxonomy', {
            'fields': ('name', 'scientific_name', 'category', 'is_active', 'image')
        }),
        ('Detailed Documentation', {
            'fields': ('description', 'morphology', 'identification_features')
        }),
        ('Traditional Literature', {
            'fields': ('traditional_uses',)
        }),
        ('Audit Metadata', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )
