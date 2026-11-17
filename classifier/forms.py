"""
Forms for the Classifier application.
Includes secure image validation, format filtering, and size bounds checking.
"""

import os
from django import forms
from django.conf import settings
from PIL import Image

class PlantImageUploadForm(forms.Form):
    image = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'id': 'image-input',
            'accept': 'image/jpeg,image/png,image/webp',
        }),
        help_text="Select or drop a clear plant leaf, flower, or stem photo (JPEG, PNG, or WEBP, max 5 MB)."
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Optional field notes (e.g., location, date collected, physical habitat)...'
        }),
        help_text="Optional context for your research record."
    )

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if not image:
            raise forms.ValidationError("No image file was provided. Please choose a valid image.")

        # 1. Size Validation (Max 5 MB)
        max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 5 * 1024 * 1024)
        if image.size > max_size:
            size_mb = max_size / (1024 * 1024)
            raise forms.ValidationError(
                f"File size exceeds the {size_mb:.0f} MB limit. Current size is {image.size / (1024 * 1024):.2f} MB."
            )

        # 2. File Extension Validation
        ext = os.path.splitext(image.name)[1].lower()
        allowed_extensions = getattr(settings, 'ALLOWED_IMAGE_EXTENSIONS', ['.jpg', '.jpeg', '.png', '.webp'])
        if ext not in allowed_extensions:
            raise forms.ValidationError(
                f"Unsupported file format '{ext}'. Permitted formats: {', '.join(allowed_extensions)}."
            )

        # 3. MIME / Pillow Integrity Verification
        try:
            # Open and verify via PIL
            image_copy = Image.open(image)
            image_copy.verify()

            # Ensure format is recognized as JPEG, PNG, or WEBP
            if image_copy.format not in ['JPEG', 'PNG', 'WEBP']:
                raise forms.ValidationError(
                    f"Unsupported image encoding: {image_copy.format}. Must be JPEG, PNG, or WEBP."
                )

            # Reset file pointer for subsequent processing
            image.seek(0)

            # Re-open to verify dimensions are reasonable (min 32x32, max 8000x8000)
            with Image.open(image) as img_check:
                width, height = img_check.size
                if width < 32 or height < 32:
                    raise forms.ValidationError("Image resolution is too small for classification (minimum 32x32).")
                if width > 8000 or height > 8000:
                    raise forms.ValidationError("Image resolution is abnormally high (maximum 8000x8000 pixels).")

            image.seek(0)
        except forms.ValidationError:
            raise
        except Exception as e:
            raise forms.ValidationError(f"Invalid or corrupted image file: {str(e)}")

        return image
