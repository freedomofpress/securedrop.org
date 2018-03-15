from wagtail.wagtailcore.models import Site

from common.models import DirectorySettings


def turn_on_instance_scanning():
    site = Site.objects.get(is_default_site=True)
    settings = DirectorySettings.for_site(site)
    settings.show_scan_results = True
    settings.save()


def turn_on_instance_management():
    site = Site.objects.get(is_default_site=True)
    settings = DirectorySettings.for_site(site)
    settings.allow_directory_management = True
    settings.save()
