# flake8: noqa: F401
# flake8: noqa: F403

" Settings for tests. "
from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
