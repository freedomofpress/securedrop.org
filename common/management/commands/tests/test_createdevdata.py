import os

from django.contrib.auth.models import User
from django.core import management
from django.test import TransactionTestCase
from django.urls import reverse
from wagtail.models import Page


class CreateDevDataTestCase(TransactionTestCase):
    def test_createdevdata_works(self):
        """The createdevdata command successfully creates functional pages

        The createdevdata management command should run successfully,
        without raising any exceptions, and the pages it generates
        should return a 200 status code when requested, edited, and
        explored in the wagtail admin.

        """
        # Write stdout to /dev/null so as not to clutter the output from the tests
        with open(os.devnull, 'w') as devnull:
            management.call_command('createdevdata', '--delete', '--no-download', stdout=devnull)

        # We expect `createdevdata` to also make a superuser
        self.client.force_login(User.objects.filter(is_superuser=True).first())

        for page in Page.objects.exclude(slug='root'):
            with self.subTest(page=page.specific):
                response = self.client.get(page.get_url())
                self.assertEqual(response.status_code, 200)

                explore_url = reverse('wagtailadmin_explore', args=(page.pk,))
                explore_response = self.client.get(explore_url)
                self.assertEqual(explore_response.status_code, 200)

                edit_url = reverse('wagtailadmin_pages:edit', args=(page.pk,))
                edit_response = self.client.get(edit_url)
                self.assertEqual(edit_response.status_code, 200)
