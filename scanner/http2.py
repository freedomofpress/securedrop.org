import socket
import ssl
from urllib.parse import urlparse


def check_http2(domain_name):
    """Check for support of the HTTP/2 protocol for a given domain.

    This function attempts to connect to the given domain over SSL,
    and records if the protocol used by the remote server is HTTP/2.
    The return value is a dictionary of ScanResult attributes
    describing if the protocol is supported or not.

    """
    socket.setdefaulttimeout(5)
    try:
        host = urlparse(domain_name).netloc
        port = 443

        ctx = ssl.create_default_context()
        ctx.set_alpn_protocols(['h2', 'spdy/3', 'http/1.1'])

        conn = ctx.wrap_socket(
            socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=host
        )
        conn.connect((host, port))

        selected_protocol = conn.selected_alpn_protocol()

        if selected_protocol == 'h2':
            return {'http2': True}
        else:
            return {'http2': False}
    except Exception:
        return {'http2': False}
