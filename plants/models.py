"""
Models for the Plants application.

Represents botanical and taxonomic information for medicinal and Ayurvedic plants.
"""

from django.db import models

class Plant(models.Model):
    CATEGORY_CHOICES = [
        ('Ayurvedic Plant', 'Ayurvedic Plant'),
        ('Medicinal Herb', 'Medicinal Herb'),
        ('Aromatic Flora', 'Aromatic Flora'),
        ('General Botanical', 'General Botanical'),
    ]

    name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        help_text="Common or vernacular name of the plant (e.g., Tulsi, Neem)."
    )
    scientific_name = models.CharField(
        max_length=200,
        db_index=True,
        help_text="Botanical binomial nomenclature (e.g., Ocimum sanctum)."
    )
    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        default='Ayurvedic Plant',
        db_index=True,
        help_text="Botanical or pharmacological classification."
    )
    description = models.TextField(
        help_text="Comprehensive overview and natural habitat of the plant species."
    )
    morphology = models.TextField(
        help_text="Structural botanical characteristics: leaf arrangement, stem, inflorescence, flowers, and fruit."
    )
    traditional_uses = models.TextField(
        help_text="Documented historical/traditional preparations in Ayurvedic literature (strictly informational)."
    )
    identification_features = models.TextField(
        help_text="Distinguishing diagnostic keys for field identification (e.g., serrated margins, venation, fragrance)."
    )
    image = models.ImageField(
        upload_to='plants/',
        blank=True,
        null=True,
        help_text="Reference botanical specimen or herbarium photograph."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Determines if this plant profile is publicly accessible in the catalog."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Plant'
        verbose_name_plural = 'Plants'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['scientific_name']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.name} ({self.scientific_name})"
