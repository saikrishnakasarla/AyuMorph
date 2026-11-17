"""
Machine Learning Configuration for AyuMorph MobileNetV2 Model.

This file centralizes all hyperparameters, image dimensions, normalization
routines, and class mappings used by the trained model.
"""

from pathlib import Path
from django.conf import settings

# Primary and fallback model file paths
MODEL_DIR = Path(settings.BASE_DIR) / 'classifier' / 'ml_model'
PRIMARY_MODEL_PATH = MODEL_DIR / 'model.h5'
FALLBACK_MODEL_PATH = MODEL_DIR / 'model.keras'

# Target input resolution expected by MobileNetV2
IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224
IMAGE_CHANNELS = 3
TARGET_SIZE = (IMAGE_WIDTH, IMAGE_HEIGHT)

# Preprocessing normalizations:
# - 'mobilenet_v2': scales pixel values to [-1.0, 1.0] via ((x / 127.5) - 1.0)
# - 'rescaling_255': scales pixel values to [0.0, 1.0] via (x / 255.0)
PREPROCESSING_MODE = 'mobilenet_v2'

# Decision threshold for binary classification
DECISION_THRESHOLD = getattr(settings, 'ML_THRESHOLD', 0.5)

# Binary Classification Mapping
# By default, Keras ImageDataGenerator sorts directory names alphabetically:
# 0 -> 'Ayurvedic Plant' (or first alphabetical class folder)
# 1 -> 'Non-Ayurvedic Plant' (or second alphabetical class folder)
#
# If your training pipeline used a different mapping, adjust below:
CLASS_MAPPING = {
    0: getattr(settings, 'CLASS_0_LABEL', 'Ayurvedic Plant'),
    1: getattr(settings, 'CLASS_1_LABEL', 'Non-Ayurvedic Plant'),
}

# Model Architecture Label for Metadata Audit
MODEL_ARCHITECTURE = "MobileNetV2 Transfer Learning (ImageNet base, GAP, Dense-128, Sigmoid-1)"
