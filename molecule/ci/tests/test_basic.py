import ssl
import os
import urllib2 as urllib


def test_mainpage(host):
    """
    Basic test to make sure home-page is coming up.
    """
    SITE_STRING = "Press Freedom Incidents"

    content = host.check_output("curl -k https://localhost:443")
    head = host.check_output("curl -I -k https://localhost:443")
    assert "Press Freedom Incidents" in content
    assert "HTTP/1.1 200 OK" in head
