import os
import sys

# Ensure root directory is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from web_app import app

class VercelMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        if path.startswith('/api/index'):
            new_path = path[10:]
            if not new_path or new_path == '.py':
                new_path = '/'
            environ['PATH_INFO'] = new_path
        return self.app(environ, start_response)

app.wsgi_app = VercelMiddleware(app.wsgi_app)
