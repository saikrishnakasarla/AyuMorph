"""
Unit tests for AyuMorph database models (accounts, plants, classifier).
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import Profile
from plants.models import Plant
from classifier.models import Prediction

class ModelTests(TestCase):
    def setUp(self):
        # Create a test researcher user
        self.user = User.objects.create_user(
            username='botanist_jane',
            email='jane@ayumorph.edu',
            password='SecurePassword123!',
            first_name='Jane',
            last_name='Doe'
        )

        # Create a reference plant
        self.plant = Plant.objects.create(
            name='Tulsi',
            scientific_name='Ocimum tenuiflorum',
            category='Ayurvedic Plant',
            description='Holy basil specimen.',
            morphology='Opposite decussate leaves.',
            traditional_uses='Documented in classical texts for seasonal respiratory comfort.',
            identification_features='Square stems and clove-like fragrance.',
            is_active=True
        )

    def test_user_profile_signal_creation(self):
        """Ensures that user creation triggers automatic Profile creation via post_save signal."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, Profile)
        self.assertEqual(str(self.user.profile), "botanist_jane Profile")

    def test_plant_model_str_and_properties(self):
        """Validates Plant string representation and attributes."""
        self.assertEqual(str(self.plant), "Tulsi (Ocimum tenuiflorum)")
        self.assertTrue(self.plant.is_active)
        self.assertEqual(self.plant.category, 'Ayurvedic Plant')

    def test_prediction_model_creation(self):
        """Validates Prediction record instantiation and computed properties."""
        test_image = SimpleUploadedFile(
            name='sample_leaf.jpg',
            content=b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb',
            content_type='image/jpeg'
        )

        prediction = Prediction.objects.create(
            user=self.user,
            plant=self.plant,
            uploaded_image=test_image,
            predicted_class='Ayurvedic Plant',
            confidence=94.52,
            raw_score=0.9452,
            prediction_status='SUCCESS',
            processing_time=0.124,
            model_version='MobileNetV2-TransferLearning'
        )

        self.assertEqual(prediction.user, self.user)
        self.assertEqual(prediction.plant, self.plant)
        self.assertTrue(prediction.is_ayurvedic)
        self.assertIn("Prediction #", str(prediction))
        self.assertIn("94.5%", str(prediction))

    def test_prediction_non_ayurvedic_property(self):
        """Validates is_ayurvedic property when class is Non-Ayurvedic."""
        prediction = Prediction.objects.create(
            user=self.user,
            uploaded_image=SimpleUploadedFile('test.jpg', b'dummy', 'image/jpeg'),
            predicted_class='Non-Ayurvedic Plant',
            confidence=88.1,
            prediction_status='SUCCESS'
        )
        self.assertFalse(prediction.is_ayurvedic)
