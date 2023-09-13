"""
WSGI config for spotify_stats_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from whitenoise import WhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spotify_stats_project.settings")

application = get_wsgi_application()

# Add WhiteNoise middleware to serve static files
application = WhiteNoise(application, root=os.path.join(os.path.dirname(__file__), 'staticfiles'))


app = application