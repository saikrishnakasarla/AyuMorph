"""
ASGI config for AyuMorph project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ayumorph.settings')

application = get_asgi_application()
