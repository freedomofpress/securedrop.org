import enum


EventCode = enum.IntEnum(
    value="EventCode",
    # New names should only be added to the *end* of this list.
    # Adding a new name will implicitly change the integer value of
    # the names that come after it, which will change how these are
    # aggregated in our log files.
    #
    # For the same reason, once an event code has been released into
    # production, it should not be removed from the list.
    names=[
        'SignatureNotSha1',
        'PostDataMissing',
        'InvalidSignature',
        'UnsupportedGithubEvent',
        'UnsupportedAction',
        'ReleaseAttributeMissing',
    ],
    # This start value is designed to be unique for the "github" app.
    # Other apps should use a different start value that does not
    # reasonably conflict with this value (e.g. 2000, 3000, and so
    # on).
    start=1000,
)
