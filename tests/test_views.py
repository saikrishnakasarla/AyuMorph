"""
Integration tests for AyuMorph views, authentication, isolation, and endpoints.
"""

import io
from PIL import Image
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from plants.models import Plant
from classifier.models import Prediction


def create_test_image(filename="test_specimen.png", size=(100, 100), color=(34, 139, 34)):
    """Helper utility generating valid in-memory PNG images for test upload."""
    file_obj = io.BytesIO()
    image = Image.new("RGB", size=size, color=color)
    image.save(file_obj, format="PNG")
    file_obj.seek(0)
    return SimpleUploadedFile(filename, file_obj.read(), content_type="image/png")


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        # User 1
        self.user1 = User.objects.create_user(
            username='researcher_one',
            email='one@ayumorph.edu',
            password='Password123!',
            first_name='Alex'
        )

        # User 2 (for user-isolation tests)
        self.user2 = User.objects.create_user(
            username='researcher_two',
            email='two@ayumorph.edu',
            password='Password123!',
            first_name='Bob'
        )

        # Reference Plant
        self.plant = Plant.objects.create(
            name='Neem',
            scientific_name='Azadirachta indica',
            category='Ayurvedic Plant',
            description='Indian lilac tree.',
            morphology='Imparipinnate compound leaves.',
            traditional_uses='Traditional external skin hygiene and cooling applications.',
            identification_features='Serrated asymmetric leaflets.',
            is_active=True
        )

        # User 1's prediction
        self.pred1 = Prediction.objects.create(
            user=self.user1,
            plant=self.plant,
            uploaded_image=create_test_image('leaf1.png'),
            predicted_class='Ayurvedic Plant',
            confidence=91.4,
            prediction_status='SUCCESS'
        )

        # User 2's prediction
        self.pred2 = Prediction.objects.create(
            user=self.user2,
            uploaded_image=create_test_image('leaf2.png'),
            predicted_class='Non-Ayurvedic Plant',
            confidence=85.0,
            prediction_status='SUCCESS'
        )

    def test_public_pages(self):
        """Verifies public accessibility of landing, about, and catalog pages."""
        # Home
        res_home = self.client.get(reverse('home'))
        self.assertEqual(res_home.status_code, 200)
        self.assertContains(res_home, 'AyuMorph')

        # About
        res_about = self.client.get(reverse('about'))
        self.assertEqual(res_about.status_code, 200)
        self.assertContains(res_about, 'MobileNetV2')

        # Plants Catalog
        res_plants = self.client.get(reverse('plants:plant_list'))
        self.assertEqual(res_plants.status_code, 200)
        self.assertContains(res_plants, 'Neem')

        # Plant Detail
        res_detail = self.client.get(reverse('plants:plant_detail', args=[self.plant.id]))
        self.assertEqual(res_detail.status_code, 200)
        self.assertContains(res_detail, 'Azadirachta indica')

    def test_authentication_registration(self):
        """Tests user registration workflow."""
        reg_data = {
            'username': 'new_student',
            'first_name': 'Student',
            'last_name': 'Tester',
            'email': 'student@university.ac.in',
            'institution': 'Dept of Information Technology',
            'password1': 'StrongPass2026!',
            'password2': 'StrongPass2026!'
        }
        response = self.client.post(reverse('register'), reg_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='new_student').exists())
        user = User.objects.get(username='new_student')
        self.assertEqual(user.profile.institution, 'Dept of Information Technology')

    def test_registration_duplicate_email_rejected(self):
        """Ensures that duplicate email registration is rejected."""
        reg_data = {
            'username': 'another_user',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'one@ayumorph.edu',  # Already used by user1
            'password1': 'StrongPass2026!',
            'password2': 'StrongPass2026!'
        }
        response = self.client.post(reverse('register'), reg_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with this email address already exists')

    def test_login_and_logout(self):
        """Tests login and logout flows."""
        login_res = self.client.post(reverse('login'), {
            'username': 'researcher_one',
            'password': 'Password123!'
        })
        self.assertEqual(login_res.status_code, 302)

        logout_res = self.client.post(reverse('logout'))
        self.assertEqual(logout_res.status_code, 302)

    def test_dashboard_access_control(self):
        """Ensures unauthenticated users are redirected to login when trying to access dashboard."""
        res_unauth = self.client.get(reverse('classifier:dashboard'))
        self.assertEqual(res_unauth.status_code, 302)
        self.assertIn('/login/', res_unauth.url)

        # Authenticate User 1
        self.client.login(username='researcher_one', password='Password123!')
        res_auth = self.client.get(reverse('classifier:dashboard'))
        self.assertEqual(res_auth.status_code, 200)
        self.assertContains(res_auth, 'researcher_one')

    def test_prediction_history_user_isolation(self):
        """
        CRITICAL SECURITY REQUIREMENT:
        User 1 should ONLY see their own predictions in history,
        and never see User 2's predictions.
        """
        self.client.login(username='researcher_one', password='Password123!')
        res = self.client.get(reverse('classifier:history'))
        self.assertEqual(res.status_code, 200)
        # User 1's prediction should be present
        self.assertContains(res, f"#AYU-{self.pred1.id:05d}")
        # User 2's prediction must NOT be present
        self.assertNotContains(res, f"#AYU-{self.pred2.id:05d}")

    def test_prediction_result_user_isolation(self):
        """
        Ensures User 1 cannot access User 2's private prediction result via direct URL.
        """
        self.client.login(username='researcher_one', password='Password123!')
        # Attempt to access User 2's result
        res = self.client.get(reverse('classifier:prediction_result', args=[self.pred2.id]))
        self.assertEqual(res.status_code, 404)

    def test_prediction_deletion_user_isolation(self):
        """
        Ensures User 1 can delete their own prediction, but cannot delete User 2's.
        """
        self.client.login(username='researcher_one', password='Password123!')

        # Attempt to delete User 2's prediction
        del_user2_res = self.client.post(reverse('classifier:prediction_delete', args=[self.pred2.id]))
        self.assertEqual(del_user2_res.status_code, 404)
        self.assertTrue(Prediction.objects.filter(id=self.pred2.id).exists())

        # Delete own prediction
        del_own_res = self.client.post(reverse('classifier:prediction_delete', args=[self.pred1.id]))
        self.assertEqual(del_own_res.status_code, 302)
        self.assertFalse(Prediction.objects.filter(id=self.pred1.id).exists())
