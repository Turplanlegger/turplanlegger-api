from flask import Flask
from flask_cors import CORS


class Cors:

    def __init__(self, app: Flask = None) -> None:
        self.app = None
        if app:
            self.init_app(app)

    def init_app(self, app: Flask = None) -> None:
        CORS(
            app,
            origins=app.config.get('CORS_ORIGINS'),
            resources=[
                '/item_lists/*',
                '/item_list/*',
                '/login/*',
                '/notes/*',
                '/note/*',
                '/tests/*',
                '/test/*',
                '/trips/*',
                '/trip/*',
                '/routes/*',
                '/route/*',
                '/users/*',
                '/user/*'
            ]
        )
