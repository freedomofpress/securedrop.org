from django.test import TestCase
from django.test import Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from allauth.account.models import EmailAddress
from landing_page_checker.tests.factories import SecuredropPageFactory
from landing_page_checker.models import SecuredropOwner


class UnauthenticatedTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.unowned_sd_page = SecuredropPageFactory()

    def test_unauthenticated_is_redirected_to_login_dashboard(self):
        response = self.client.get(reverse_lazy('dashboard'), follow=True)
        # gets last address directed to and removes queries
        response_last_address = response.redirect_chain[-1][0].split('?')[0]
        self.assertEqual(response_last_address, reverse_lazy('account_login'))

    def test_unauthenticated_is_redirected_to_login_details(self):
        slug = self.unowned_sd_page.slug
        response = self.client.get(
            reverse_lazy('securedrop_detail', kwargs={'slug': slug}),
            follow=True,
        )
        response_last_address = response.redirect_chain[-1][0].split('?')[0]
        self.assertEqual(response_last_address, reverse_lazy('account_login'))


class AuthenticatedTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        self.username = "Rachel"
        self.email = "r@r.com"
        self.password = "rachel"
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password, is_active=True)
        self.user.save()
        # Create a verified email address object for this user via allauth
        EmailAddress.objects.create(user=self.user, email=self.email, verified=True)

        self.unowned_sd_page = SecuredropPageFactory()
        self.unowned_sd_page.save()
        self.user_owned_sd_page = SecuredropPageFactory()
        self.user_owned_sd_page.save()
        SecuredropOwner(owner=self.user, page=self.user_owned_sd_page).save()
        # Login
        self.client.post(reverse_lazy('account_login'), {'login': self.email, 'password': self.password})

    def test_authenticated_user_can_view_dashboard(self):
        response2 = self.client.get(reverse_lazy('dashboard'))
        self.assertEqual(response2.status_code, 200)

    def test_authenticated_user_can_view_their_instances(self):
        slug = self.user_owned_sd_page.slug
        response = self.client.get(reverse_lazy('securedrop_detail', kwargs={'slug': slug}))
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_cannot_view_other_instances(self):
        slug = self.unowned_sd_page.slug
        response = self.client.get(reverse_lazy('securedrop_detail', kwargs={'slug': slug}))
        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_can_edit_their_instances(self):
        new_title = 'New'
        slug = self.user_owned_sd_page.slug
        response = self.client.post(
            reverse_lazy('securedrop_detail', kwargs={'slug': slug}),
            {
                'title': new_title,
                # The autocomplete widget parses the below form values
                # as JSON, and 'null' is the least obtrusive value to
                # send.
                'languages': 'null',
                'topics': 'null',
                'countries': 'null',
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_cannot_edit_other_instances(self):
        new_title = 'New'
        slug = self.unowned_sd_page.slug
        response = self.client.post(
            reverse_lazy('securedrop_detail', kwargs={'slug': slug}),
            {
                'title': new_title,
                # The autocomplete widget parses the below form values
                # as JSON, and 'null' is the least obtrusive value to
                # send.
                'languages': 'null',
                'topics': 'null',
                'countries': 'null',
            }
        )
        self.assertEqual(response.status_code, 403)
