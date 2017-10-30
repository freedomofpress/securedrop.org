from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.test import Client
from django.test import TestCase
from allauth.account.models import EmailAddress
from directory.tests.factories import DirectoryPageFactory
from landing_page_checker.models import SecuredropOwner
from landing_page_checker.tests.factories import SecuredropPageFactory
from wagtail.wagtailcore.models import Site


class SecuredropPageTest(TestCase):
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
        # Setup pages. Site is needed for valid urls.
        site = Site.objects.get()
        directory = DirectoryPageFactory(parent=site.root_page)
        self.unowned_sd_page = SecuredropPageFactory(live=True, parent=directory)
        self.unowned_sd_page.save()
        self.user_owned_sd_page = SecuredropPageFactory(live=True, parent=directory)
        self.user_owned_sd_page.save()
        SecuredropOwner(owner=self.user, page=self.user_owned_sd_page).save()

    def test_logged_in_user_should_see_edit_on_owned_pages(self):
        # Login
        self.client.post(reverse_lazy('account_login'), {'login': self.email, 'password': self.password})
        response = self.client.get(self.user_owned_sd_page.url)
        self.assertTrue(response.context['page'].editable)

    def test_logged_out_user_should_not_see_edit(self):
        response = self.client.get(self.user_owned_sd_page.url)
        self.assertFalse(response.context['page'].editable)

    def test_logged_in_user_should_not_see_edit_on_unowned_pages(self):
        self.client.post(reverse_lazy('account_login'), {'login': self.email, 'password': self.password})
        response = self.client.get(self.unowned_sd_page.url)
        self.assertFalse(response.context['page'].editable)
