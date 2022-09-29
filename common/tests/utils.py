from wagtail.core.models import Site

from directory.models import DirectorySettings


def turn_on_instance_scanning():
    site = Site.objects.get(is_default_site=True)
    settings = DirectorySettings.for_site(site)
    settings.show_scan_results = True
    settings.save()
