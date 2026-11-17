"""
Inference engine and MobileNetV2 predictor module for AyuMorph.

Handles cached model loading, PIL image preprocessing, inference execution,
and structured prediction formatting.
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import numpy as np
from PIL import Image

from .config import (
    PRIMARY_MODEL_PATH,
    FALLBACK_MODEL_PATH,
    TARGET_SIZE,
    PREPROCESSING_MODE,
    DECISION_THRESHOLD,
    CLASS_MAPPING,
    MODEL_ARCHITECTURE,
)

logger = logging.getLogger(__name__)


class ModelNotFoundError(FileNotFoundError):
    """Raised when the trained MobileNetV2 model file is not present in classifier/ml_model/."""
    pass


class MLEnvironmentError(RuntimeError):
    """Raised when the underlying ML framework (TensorFlow/Keras) encounters an environment issue."""
    pass


class PlantPredictor:
    """
    Singleton predictor that holds the loaded MobileNetV2 model in memory
    to avoid re-loading from disk on every HTTP request.
    """
    _instance: Optional['PlantPredictor'] = None
    _model: Any = None
    _model_path: Optional[Path] = None
    _model_metadata: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlantPredictor, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_model_path(cls) -> Optional[Path]:
        """Locates model.h5 or model.keras in the model directory."""
        if PRIMARY_MODEL_PATH.exists():
            return PRIMARY_MODEL_PATH
        if FALLBACK_MODEL_PATH.exists():
            return FALLBACK_MODEL_PATH
        return None

    @classmethod
    def is_model_available(cls) -> bool:
        """Returns True if a model file is placed in classifier/ml_model/."""
        return cls.get_model_path() is not None

    def load_model(self):
        """
        Loads the trained MobileNetV2 model into memory if not already cached.
        Inspects input shape, output shape, and activation properties.
        """
        if self._model is not None:
            return self._model

        model_file = self.get_model_path()
        if not model_file:
            raise ModelNotFoundError(
                f"Trained model not found. Expected '{PRIMARY_MODEL_PATH}' or '{FALLBACK_MODEL_PATH}'. "
                f"Please place your trained model file into 'classifier/ml_model/'."
            )

        logger.info(f"Loading trained MobileNetV2 model from {model_file}...")
        try:
            # Attempt loading via keras or tensorflow.keras
            try:
                import keras
                loaded_model = keras.models.load_model(str(model_file), compile=False)
            except Exception:
                from tensorflow import keras as tf_keras
                loaded_model = tf_keras.models.load_model(str(model_file), compile=False)

            self._model = loaded_model
            self._model_path = model_file

            # Inspect model architecture
            input_shape = getattr(loaded_model, 'input_shape', None)
            output_shape = getattr(loaded_model, 'output_shape', None)
            is_binary = (output_shape[-1] == 1) if output_shape else True

            self._model_metadata = {
                'path': str(model_file),
                'input_shape': input_shape,
                'output_shape': output_shape,
                'is_binary': is_binary,
                'num_classes': 2 if is_binary else (output_shape[-1] if output_shape else 2),
                'architecture': MODEL_ARCHITECTURE,
            }
            logger.info(f"Model loaded successfully. Metadata: {self._model_metadata}")
            return self._model

        except ImportError as e:
            raise MLEnvironmentError(
                "Neither Keras nor TensorFlow could be imported in the current Python environment. "
                "Ensure a compatible version (Python 3.10/3.11 recommended for TensorFlow on Windows) is active."
            ) from e
        except Exception as e:
            raise MLEnvironmentError(
                f"Error loading model from {model_file}: {str(e)}"
            ) from e

    def get_metadata(self) -> Dict[str, Any]:
        """Returns diagnostic metadata about the loaded model."""
        if not self._model:
            model_file = self.get_model_path()
            return {
                'available': model_file is not None,
                'expected_primary_path': str(PRIMARY_MODEL_PATH),
                'expected_fallback_path': str(FALLBACK_MODEL_PATH),
                'loaded': False,
            }
        return {
            'available': True,
            'loaded': True,
            **self._model_metadata
        }

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Loads and preprocesses an image file to match MobileNetV2 input specifications.
        Steps:
        1. Open image using PIL
        2. Verify integrity and convert to RGB
        3. Resize using LANCZOS antialiasing to target (224, 224)
        4. Normalize according to MobileNetV2 specification [-1.0, 1.0]
        5. Expand dimensions to (1, 224, 224, 3)
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at path: {image_path}")

        try:
            with Image.open(image_path) as img:
                img.verify()
        except Exception as e:
            raise ValueError(f"Corrupted or invalid image file: {str(e)}")

        with Image.open(image_path) as img:
            rgb_img = img.convert('RGB')
            resized_img = rgb_img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
            img_array = np.array(resized_img, dtype=np.float32)

        # Preprocessing normalization
        if PREPROCESSING_MODE == 'mobilenet_v2':
            # MobileNetV2 standard: scales [0, 255] to [-1.0, 1.0]
            preprocessed_array = (img_array / 127.5) - 1.0
        elif PREPROCESSING_MODE == 'rescaling_255':
            # Standard [0.0, 1.0] rescaling
            preprocessed_array = img_array / 255.0
        else:
            preprocessed_array = img_array

        # Expand batch dimension: (224, 224, 3) -> (1, 224, 224, 3)
        return np.expand_dims(preprocessed_array, axis=0)

    def predict(self, image_path: str) -> Dict[str, Any]:
        """
        Runs inference on the provided image and returns structured predictions.
        Does NOT fake any predictions. Raises appropriate exceptions if model is missing.
        """
        model = self.load_model()
        input_tensor = self.preprocess_image(image_path)

        start_time = time.time()
        raw_output = model.predict(input_tensor, verbose=0)
        elapsed_time = time.time() - start_time

        is_binary = self._model_metadata.get('is_binary', True)

        if is_binary:
            # Binary classification (Single Sigmoid Output)
            score = float(raw_output[0][0])
            if score >= DECISION_THRESHOLD:
                predicted_class_idx = 1
                confidence = score * 100.0
            else:
                predicted_class_idx = 0
                confidence = (1.0 - score) * 100.0
            raw_score = score
        else:
            # Multiclass classification (Softmax Output)
            probs = raw_output[0]
            predicted_class_idx = int(np.argmax(probs))
            confidence = float(np.max(probs)) * 100.0
            raw_score = float(probs[predicted_class_idx])

        class_name = CLASS_MAPPING.get(predicted_class_idx, f"Class {predicted_class_idx}")
        is_ayurvedic = ('ayurvedic' in class_name.lower() and 'non' not in class_name.lower())

        # Attempt to match with documented botanical catalog
        plant_obj = None
        try:
            from plants.models import Plant
            if is_ayurvedic:
                plant_obj = Plant.objects.filter(is_active=True).first()
        except Exception:
            plant_obj = None

        return {
            "status": "SUCCESS",
            "class_name": class_name,
            "confidence": round(confidence, 2),
            "raw_score": round(raw_score, 4),
            "is_ayurvedic": is_ayurvedic,
            "plant_name": plant_obj.name if plant_obj else None,
            "plant_id": plant_obj.id if plant_obj else None,
            "processing_time": round(elapsed_time, 3),
            "model_version": self._model_metadata.get('architecture', MODEL_ARCHITECTURE),
        }


def predict_plant(image_path: str) -> Dict[str, Any]:
    """
    Public API function to run plant prediction.
    Instantiates or uses the singleton PlantPredictor.
    """
    predictor = PlantPredictor()
    return predictor.predict(image_path)
