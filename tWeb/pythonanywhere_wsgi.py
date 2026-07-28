# =============================================================================
# PythonAnywhere WSGI config for tradingWeb (Django)
# =============================================================================
#
# HOW TO USE (PythonAnywhere free tier — no credit card required):
#
# 1. Sign up at https://www.pythonanywhere.com  (Beginner / free account)
#
# 2. Dashboard → "Files" tab → upload the whole tWeb/ project folder here:
#       /home/<your-username>/mysite/tWeb/   (i.e. settings.py lives at
#       /home/<your-username>/mysite/tWeb/tWeb/settings.py)
#    Easiest: use the Bash console on PythonAnywhere and clone your GitHub repo:
#       cd ~ && git clone https://github.com/AnsonCheung1020/tradingWeb.git mysite
#
# 3. Dashboard → "Web" tab → Add a new web app → Manual config → Python 3.10
#
# 4. Set "Source code" directory to:  /home/<your-username>/mysite/tWeb
#
# 5. Open the WSGI file (Web tab → link under "Code"), delete everything,
#    and paste THIS WHOLE FILE. Replace <your-username> below.
#
# 6. Web tab → "Virtualenv" → enter your venv path, or use the system Python
#    and pip-install the requirements in a Bash console:
#       pip3.10 install -r ~/mysite/tWeb/requirements.txt
#
# 7. Web tab → "Static files" add these two mappings:
#       URL: /static/   Directory: /home/<your-username>/mysite/tWeb/assets
#       URL: /media/    Directory: /home/<your-username>/mysite/tWeb/media
#    Then in a Bash console run:
#       cd ~/mysite/tWeb && python3.10 manage.py collectstatic --noinput
#       cd ~/mysite/tWeb && python3.10 manage.py migrate
#
# 8. Web tab → Reload, then open your free URL:
#       https://<your-username>.pythonanywhere.com
#
# =============================================================================

import os
import sys

# --- IMPORTANT: replace <your-username> with your actual PythonAnywhere username
project_root = '/home/<your-username>/mysite/tWeb'

# Add the project to Python's import path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Point Django at the settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'tWeb.settings'
# Production: never run with DEBUG on
os.environ.setdefault('DEBUG', '0')
# Allow this app to be served from the pythonanywhere.com host
os.environ.setdefault('ALLOWED_HOSTS', '.pythonanywhere.com')

# Honour the X-Forwarded-Proto header so Django knows it's behind HTTPS
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()