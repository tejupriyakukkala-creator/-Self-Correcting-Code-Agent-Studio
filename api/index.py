import os
import sys

# Ensure root directory is on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from web_app import app
except ModuleNotFoundError:
    from self_correcting_agent.web_app import app

# Export top-level WSGI app for Vercel
app = app
