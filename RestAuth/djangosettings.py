# This file is part of RestAuth (http://fs.fsinf.at/wiki/RestAuth).
#
# RestAuth is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RestAuth is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RestAuth.  If not, see <http://www.gnu.org/licenses/>.
#
###############################
### Default Django settings ###
###############################

# This file is used to set some defaults usually not interesting for someone
# who wants to use RestAuth.
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = ()

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'RestAuth.common.middleware.ExceptionMiddleware',
    'RestAuth.common.middleware.LoggingMiddleware',
    'RestAuth.common.middleware.HeaderMiddleware',
]

CACHE_MIDDLEWARE_SECONDS = 300
CACHE_MIDDLEWARE_KEY_PREFIX = ''

ROOT_URLCONF = 'RestAuth.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
#    'django.contrib.sessions',
    'RestAuth.Services',
    'RestAuth.Users',
    'RestAuth.Groups',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.RemoteUserBackend',
    'RestAuth.Services.backend.InternalAuthenticationBackend',
)

#############################################
### Defaults for the standard settings.py ###
#############################################
SKIP_VALIDATORS = [ 'linux', 'windows' ]
MIN_USERNAME_LENGTH = 3
MIN_PASSWORD_LENGTH = 6
HASH_ALGORITHM = 'sha512'
LOG_LEVEL = 'CRITICAL'
LOG_TARGET = 'stderr'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''
