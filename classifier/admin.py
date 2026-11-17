"""
Admin configuration for the Classifier application.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Prediction

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'image_thumbnail',
        'user',
        'predicted_class',
        'formatted_confidence',
        'plant',
        'prediction_status',
        'processing_time_display',
        'created_at',
    )
    list_filter = ('predicted_class', 'prediction_status', 'created_at', 'model_version')
    search_fields = ('user__username', 'predicted_class', 'plant__name', 'notes')
    ordering = ('-created_at',)
    readonly_fields = (
        'user',
        'uploaded_image',
        'predicted_class',
        'confidence',
        'raw_score',
        'prediction_status',
        'processing_time',
        'model_version',
        'created_at',
        'image_preview'
    )

    fieldsets = (
        ('Inference Record', {
            'fields': ('user', 'image_preview', 'uploaded_image')
        }),
        ('Classification Results', {
            'fields': ('predicted_class', 'confidence', 'raw_score', 'plant', 'prediction_status')
        }),
        ('Performance & Diagnostics', {
            'fields': ('processing_time', 'model_version', 'created_at', 'notes')
        }),
    )

    def image_thumbnail(self, obj):
        if obj.uploaded_image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 6px;" />',
                obj.uploaded_image.url
            )
        return "-"
    image_thumbnail.short_description = "Sample"

    def image_preview(self, obj):
        if obj.uploaded_image:
            return format_html(
                '<img src="{}" style="max-width: 320px; max-height: 320px; border-radius: 8px;" />',
                obj.uploaded_image.url
            )
        return "-"
    image_preview.short_description = "Image Preview"

    def formatted_confidence(self, obj):
        badge_class = "success" if obj.is_ayurvedic else "secondary"
        return format_html(
            '<span class="badge bg-{}">{:.1f}%</span>',
            badge_class,
            obj.confidence
        )
    formatted_confidence.short_description = "Confidence"

    def processing_time_display(self, obj):
        if obj.processing_time is not None:
            return f"{obj.processing_time:.3f}s"
        return "-"
    processing_time_display.short_description = "Inference Time"
