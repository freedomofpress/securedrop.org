from django.test import TestCase
from django.test import Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy


class LoginTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        self.username = "Rachel"
        self.email = "r@r.com"
        self.password = "rachel"
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password, is_active=True)
        self.user.save()

    def test_unauthenticated_is_redirected_to_login(self):
        response = self.client.get(reverse_lazy('dashboard'), follow=True)
        # gets last address directed to and removes queries
        response_last_address = response.redirect_chain[-1][0].split('?')[0]
        self.assertEqual(response_last_address, reverse_lazy('account_login'))

    def test_authenticated_user_can_view_dashboard(self):
        print(get_user_model().objects.all())
        response1 = self.client.post(reverse_lazy('account_login'), {'login': self.email, 'password': self.password })
        print([template.name for template in response1.templates])
        response2 = self.client.get(reverse_lazy('dashboard'))

        print(response2)
        self.assertEqual(response2.status_code, 200)
