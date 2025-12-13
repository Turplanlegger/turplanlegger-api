from urllib.parse import urljoin

from flask import request

from turplanlegger.utils.config import config


def absolute_url(path: str = '') -> str:
    try:
        base_url = config.base_url or request.url_root
    except Exception:
        base_url = '/'
    return urljoin(base_url + '/', path.lstrip('/')) if path else base_url
