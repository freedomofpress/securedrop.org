from unittest.mock import patch

from django.test import TestCase

from menus.models import Menu, MenuItem


@patch('menus.signals.purge_all_from_cache')
class FrontendCacheTestCase(TestCase):
    def test_new_menu_purges_cache(self, purge_mock):
        "Creating a new menu should purge the entire zone"
        Menu.objects.create(name='Test Menu', slug='test-menu')
        self.assertEqual(purge_mock.call_count, 1)

    def test_delete_menu_purges_cache(self, purge_mock):
        "Deleting a menu should purge the entire zone"
        menu = Menu.objects.create(name='Test Menu', slug='test-menu')
        purge_mock.reset_mock()

        menu.delete()
        self.assertEqual(purge_mock.call_count, 1)

    def test_new_menu_item_purges_cache(self, purge_mock):
        "Creating a new menu item should purge the entire zone"
        menu = Menu.objects.create(name='Test Menu', slug='test-menu')
        purge_mock.reset_mock()

        MenuItem.objects.create(text='Test Item', menu=menu)
        self.assertEqual(purge_mock.call_count, 1)

    def test_update_menu_item_purges_cache(self, purge_mock):
        "Changing a menu item should purge the entire zone"
        menu = Menu.objects.create(name='Test Menu', slug='test-menu')
        menu_item = MenuItem.objects.create(text='Test Item', menu=menu)
        purge_mock.reset_mock()

        menu_item.text = 'New Text'
        menu_item.save()
        self.assertEqual(purge_mock.call_count, 1)

    def test_delete_menu_item_purges_cache(self, purge_mock):
        "Deleting a menu item should purge the entire zone"
        menu = Menu.objects.create(name='Test Menu', slug='test-menu')
        menu_item = MenuItem.objects.create(text='Test Item', menu=menu)
        purge_mock.reset_mock()

        menu_item.delete()
        self.assertEqual(purge_mock.call_count, 1)
