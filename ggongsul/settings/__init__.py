import os

APP_ENV = os.environ.get('APP_ENV', 'production')
if APP_ENV == 'development':
    from .development import *
else:
    from .production import *
