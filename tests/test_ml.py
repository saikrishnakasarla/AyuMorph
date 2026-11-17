"""
Unit tests for Machine Learning preprocessing, predictor singleton, and inference routines.
"""

import os
import tempfile
import numpy as np
from PIL import Image
from unittest.mock import MagicMock, patch
from django.test import TestCase

from classifier.ml.predictor import (
    PlantPredictor,
    ModelNotFoundError,
    predict_plant
)
from classifier.ml.config import TARGET_SIZE


class MLPredictorTests(TestCase):
    def setUp(self):
        # Create a real temporary test image on disk
        self.temp_dir = tempfile.mkdtemp()
        self.image_path = os.path.join(self.temp_dir, 'sample_herb.png')
        img = Image.new('RGB', (320, 240), color=(40, 140, 60))
        img.save(self.image_path, format='PNG')

    def tearDown(self):
        # Clean up temporary file and directory
        if os.path.exists(self.image_path):
            os.remove(self.image_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_predictor_singleton(self):
        """Ensures PlantPredictor follows a strict singleton pattern."""
        p1 = PlantPredictor()
        p2 = PlantPredictor()
        self.assertIs(p1, p2)

    def test_image_preprocessing_shape_and_bounds(self):
        """
        Validates MobileNetV2 preprocessing:
        - Image is resized to (224, 224)
        - Batch dimension added: (1, 224, 224, 3)
        - Normalized to [-1.0, 1.0]
        - Output dtype is float32
        """
        predictor = PlantPredictor()
        tensor = predictor.preprocess_image(self.image_path)

        self.assertIsInstance(tensor, np.ndarray)
        self.assertEqual(tensor.shape, (1, 224, 224, 3))
        self.assertEqual(tensor.dtype, np.float32)
        # MobileNetV2 normalization bounds check: [-1.0, 1.0]
        self.assertTrue(np.all(tensor >= -1.05))
        self.assertTrue(np.all(tensor <= 1.05))

    def test_corrupted_image_preprocessing_error(self):
        """Ensures corrupted image files raise a ValueError during preprocessing."""
        corrupted_path = os.path.join(self.temp_dir, 'corrupt.jpg')
        with open(corrupted_path, 'wb') as f:
            f.write(b'NOT_A_REAL_IMAGE_BYTES')

        predictor = PlantPredictor()
        with self.assertRaises(ValueError):
            predictor.preprocess_image(corrupted_path)

        if os.path.exists(corrupted_path):
            os.remove(corrupted_path)

    def test_missing_model_raises_model_not_found(self):
        """
        Ensures that when no model is placed in classifier/ml_model/,
        load_model raises ModelNotFoundError instead of fabricating results.
        """
        predictor = PlantPredictor()
        # Reset any cached model for test
        predictor._model = None

        with patch.object(PlantPredictor, 'get_model_path', return_value=None):
            with self.assertRaises(ModelNotFoundError):
                predictor.load_model()

    def test_mock_binary_inference_pipeline(self):
        """
        Tests complete inference pipeline using a mock MobileNetV2 model.
        Simulates sigmoid output < 0.5 (Ayurvedic Plant) and >= 0.5 (Non-Ayurvedic Plant).
        """
        predictor = PlantPredictor()
        predictor._model_metadata = {'is_binary': True, 'architecture': 'MobileNetV2-Test'}

        # Case 1: Mock sigmoid output = 0.15 (< 0.5 threshold -> Ayurvedic Plant, 85% confidence)
        mock_model_1 = MagicMock()
        mock_model_1.predict.return_value = np.array([[0.15]], dtype=np.float32)

        with patch.object(predictor, 'load_model', return_value=mock_model_1):
            result = predictor.predict(self.image_path)

            self.assertEqual(result["status"], "SUCCESS")
            self.assertEqual(result["class_name"], "Ayurvedic Plant")
            self.assertAlmostEqual(result["confidence"], 85.0, places=1)
            self.assertTrue(result["is_ayurvedic"])
            self.assertIn("processing_time", result)

        # Case 2: Mock sigmoid output = 0.92 (>= 0.5 threshold -> Non-Ayurvedic Plant, 92% confidence)
        mock_model_2 = MagicMock()
        mock_model_2.predict.return_value = np.array([[0.92]], dtype=np.float32)

        with patch.object(predictor, 'load_model', return_value=mock_model_2):
            result2 = predictor.predict(self.image_path)

            self.assertEqual(result2["status"], "SUCCESS")
            self.assertEqual(result2["class_name"], "Non-Ayurvedic Plant")
            self.assertAlmostEqual(result2["confidence"], 92.0, places=1)
            self.assertFalse(result2["is_ayurvedic"])
