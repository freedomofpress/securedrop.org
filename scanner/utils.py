def url_to_domain(url: str) -> str:
    # Split off the protocol
    if len(url.split('//')) > 1:
        url = url.split('//')[1]
    # Split off any subpath
    url = url.split('/')[0]
    return url
