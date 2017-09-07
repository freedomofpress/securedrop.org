testinfra_hosts = ["docker://sd_django"]


def test_pshtt_installed(host):
    """
    We need the pshtt library for the SecureDrop Directory, for querying
    the HTTPS configuration on Landing Pages. The pshtt module recently
    received python3 support, so we install it alongside the other
    webapp pip dependencies, inside a virtualenv

    Therefore we must run the binary from its path on disk within the
    virtualenv. By checking the `--version` output, we can confirm
    that the binary executes OK. Common problems preventing success:

      * lack of PaX flags on Python interpreter (grsecurity only)
      * elasticsearch version conflicts (due to django-json-logging)

    The following checks confirm the above.
    """
    pshtt_binary = host.file("/usr/local/bin/pshtt")
    assert pshtt_binary.exists
    assert host.check_output(pshtt_binary.path + " --version") \
            == "v0.0.1"
