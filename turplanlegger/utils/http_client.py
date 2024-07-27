import httpx
from flask import Flask


class HttpClient:
    def __init__(self, app: Flask = None) -> None:
        self.app = None
        if app:
            self.init_app(app)

    def init_app(self, app: Flask = None) -> None:
        app.http_client = httpx.Client()
