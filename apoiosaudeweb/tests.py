from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class SimpleUserTests(TestCase):
    def setUp(self):
        self.existing_user = User.objects.create_user(username='existinguser', email='existing@example.com', password='$Admin123')
        self.medico_user = User.objects.create_user(username='medicouser', email='medico@example.com', password='$Admin123', user_type='medico')

    def test_login_existing_user(self):
        login = self.client.login(username='existinguser', password='$Admin123')
        self.assertTrue(login)
        response = self.client.get(reverse('index'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_access_page_without_permission(self):
        self.client.login(username='medicouser', password='$Admin123')
        response = self.client.get(reverse('nota_list'), follow=True)
        self.assertEqual(response.status_code, 403)

    @override_settings(DEBUG=False)
    def test_404_page(self):
        response = self.client.get('/nonexistent_page/', follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'errors/404.html')
