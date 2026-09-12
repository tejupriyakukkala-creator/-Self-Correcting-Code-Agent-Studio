import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from web_app import app
except ModuleNotFoundError:
    from self_correcting_agent.web_app import app

handler = app
