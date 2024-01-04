import contextlib

import structlog
from wagtail.models import Site

from directory.models import DirectorySettings


def turn_on_instance_scanning():
    site = Site.objects.get(is_default_site=True)
    settings = DirectorySettings.for_site(site)
    settings.show_scan_results = True
    settings.save()


@contextlib.contextmanager
def capture_logs_with_contextvars():
    """Modified version of structlog.testing.capture_logs that captures
    data bound to structlog's loggers with ``bind_contextvars``.

    """
    cap = structlog.testing.LogCapture()
    old_processors = structlog.get_config()['processors']
    try:
        structlog.configure(processors=[structlog.contextvars.merge_contextvars, cap])
        yield cap.entries
    finally:
        structlog.configure(processors=old_processors)
