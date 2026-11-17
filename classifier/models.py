"""
Models for the Classifier application.
Represents botanical prediction queries and classification audit logs.
"""

from django.db import models
from django.contrib.auth.models import User
from plants.models import Plant

class Prediction(models.Model):
    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending Processing'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='predictions',
        help_text="Authenticated user who submitted the image."
    )
    plant = models.ForeignKey(
        Plant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='predictions',
        help_text="Associated reference botanical species (if identified as Ayurvedic)."
    )
    uploaded_image = models.ImageField(
        upload_to='plant_images/%Y/%m/',
        help_text="Stored original user plant photo."
    )
    predicted_class = models.CharField(
        max_length=150,
        help_text="Classification label produced by the MobileNetV2 model."
    )
    confidence = models.FloatField(
        help_text="Model statistical confidence percentage (0.00% - 100.00%)."
    )
    raw_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Unprocessed sigmoid or softmax output probability (0.0 - 1.0)."
    )
    prediction_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SUCCESS',
        help_text="Inference lifecycle status."
    )
    processing_time = models.FloatField(
        null=True,
        blank=True,
        help_text="Duration in seconds taken by the inference pipeline."
    )
    model_version = models.CharField(
        max_length=100,
        default="MobileNetV2-TransferLearning",
        help_text="Model checkpoint or architecture descriptor."
    )
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Optional user notes or field observations."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when the inference request was executed."
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Plant Prediction'
        verbose_name_plural = 'Plant Predictions'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['predicted_class']),
        ]

    def __str__(self):
        return f"Prediction #{self.id} - {self.predicted_class} ({self.confidence:.1f}%)"

    @property
    def is_ayurvedic(self):
        """Returns True if the classified label indicates an Ayurvedic plant."""
        label = self.predicted_class.lower()
        return 'ayurvedic' in label and 'non' not in label
