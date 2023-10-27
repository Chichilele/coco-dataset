def urlify(url: str) -> str:
    """Make sure url doesn't end with '/'"""
    if url.endswith("/"):
        url = url[:-1]
    return url
