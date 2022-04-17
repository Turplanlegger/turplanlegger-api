from urllib.parse import urljoin

from flask import current_app, request


def absolute_url(path: str = '') -> str:
    try:
        base_url = current_app.config.get('BASE_URL') or request.url_root
    except Exception:
        base_url = '/'
    return urljoin(base_url + '/', path.lstrip('/')) if path else base_url
