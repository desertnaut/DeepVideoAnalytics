"""
Django settings for dva project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os, dj_database_url, sys, logging

DVA_PRIVATE_ENABLE = 'DVA_PRIVATE_ENABLE' in os.environ
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_BUCKET = os.environ.get('MEDIA_BUCKET', None)
CLOUD_FS_PREFIX = os.environ.get('CLOUD_FS_PREFIX', 's3') # By default AWS "s3", Tensorflow also supports "gs" for GCS
ENABLE_CLOUDFS = os.environ.get('ENABLE_CLOUDFS',False)

if ENABLE_CLOUDFS and (MEDIA_BUCKET is None):
    raise EnvironmentError("Either data volume (do not enable cloud fs) or a remote S3/GCS bucket is required!")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']
AUTH_DISABLED = os.environ.get('AUTH_DISABLED', False)

INTERNAL_IPS = ['localhost','127.0.0.1']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = 'ENABLE_DEBUG' in os.environ

if 'ALLOWED_HOSTS' in os.environ:
    ALLOWED_HOSTS = [k.strip() for k in os.environ['ALLOWED_HOSTS'].split(',') if k.strip()]
    # SESSION_COOKIE_SECURE = True
    # CSRF_COOKIE_SECURE = True
    # SECURE_SSL_REDIRECT = True
    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') # Confirm this cannot be spoofed
    # SECURE_REDIRECT_EXEMPT = [r'^vdn/.']
else:
    ALLOWED_HOSTS = ["*"]  # Dont use this in prod

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'django-db'
WSGI_APPLICATION = 'dva.wsgi.application'
ROOT_URLCONF = 'dva.urls'

INSTALLED_APPS = [
                     'django.contrib.admin',
                     'django.contrib.auth',
                     'django.contrib.contenttypes',
                     'django.contrib.sessions',
                     'django.contrib.messages',
                     'django.contrib.staticfiles',
                     'dvaapp',
                     'dvaui',
                     'django.contrib.humanize',
                     'django.contrib.postgres',
                     'django_celery_results',
                     'corsheaders',
                     'rest_framework',
                     'django_filters',
                     'crispy_forms',
                     'rest_framework.authtoken',
                     'django_celery_beat'
                 ] + (['dvap', ] if DVA_PRIVATE_ENABLE else [])+ (['debug_toolbar'] if DEBUG else [])


MIDDLEWARE_CLASSES = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


def show_toolbar(request):
    return DEBUG


if DEBUG:
    MIDDLEWARE_CLASSES = ['debug_toolbar.middleware.DebugToolbarMiddleware',] + MIDDLEWARE_CLASSES
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': 'dva.settings.show_toolbar',
        # Rest of config
    }
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_METHODS = ('POST', 'GET',)
CORS_ALLOW_CREDENTIALS = True
CORS_URLS_REGEX = r'^api/.*$'
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

PATH_PROJECT = os.path.realpath(os.path.dirname(__file__))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
if 'BROKER_URL' in os.environ:
    BROKER_URL = os.environ['BROKER_URL']
elif 'CONTINUOUS_INTEGRATION' in os.environ:
    BROKER_URL = 'amqp://{}:{}@localhost//'.format('guest', 'guest')
else:
    BROKER_URL = 'amqp://{}:{}@{}//'.format(os.environ.get('RABBIT_USER', 'dvauser'),
                                            os.environ.get('RABBIT_PASS', 'localpass'),
                                            os.environ.get('RABBIT_HOST', 'rabbit'))

if 'DATABASE_URL' in os.environ:
    DATABASES = {}
    db_from_env = dj_database_url.config(conn_max_age=500)
    DATABASES['default'] = db_from_env
elif 'CONTINUOUS_INTEGRATION' in os.environ or sys.platform == 'darwin':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'postgres',
            'USER': 'postgres',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('DB_NAME', 'postgres'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASS', 'postgres'),
            'HOST': os.environ.get('DB_HOST', 'db'),
            'PORT': 5432,
        }
    }

REDIS_HOST = os.environ.get('REDIS_HOST','localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD','')
# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
MEDIA_ROOT = os.path.expanduser('~/media/') if sys.platform == 'darwin' or os.environ.get('TRAVISTEST',False) else "/root/media/"

if ENABLE_CLOUDFS and ('LAUNCH_SERVER' in os.environ or 'LAUNCH_SERVER_NGINX' in os.environ) and 'MEDIA_URL' not in os.environ:
    raise EnvironmentError('You must set MEDIA_URL (e.g. http://s3bucketname.s3-website-us-east-1.amazonaws.com/)'
                           ' or similar google storage bucket URL when launching websever in NFS disabled mode.')

MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')
STATIC_URL = os.environ.get('STATIC_URL', '/static/')
DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# following should be set or un-set on ALL workers
GLOBAL_MODEL_QUEUE_ENABLED = os.environ.get('GLOBAL_MODEL',False)
GLOBAL_RETRIEVER_QUEUE_ENABLED = False if os.environ.get('DISABLE_GLOBAL_RETRIEVER',False) else True

Q_MANAGER = 'qmanager'
Q_REDUCER = 'qreducer'
Q_EXTRACTOR = 'qextract'
Q_STREAMER = 'qstreamer'
Q_TRAINER = 'qtrainer'
Q_LAMBDA = 'qlambda'
GLOBAL_MODEL_FLASK_SERVER_PORT = 8989
GLOBAL_MODEL = 'qglobal_model'  # if a model specific queue does not exists then this is where the task ends up
GLOBAL_RETRIEVER = 'qglobal_retriever' # if a retriever specific queue does not exists then the task ends up here
DEFAULT_REDUCER_TIMEOUT_SECONDS = 60 # Reducer tasks checks every 60 seconds if map tasks are finished.

TASK_NAMES_TO_QUEUE = {
    "perform_process_monitoring":Q_REDUCER,
    "perform_training_set_creation":Q_EXTRACTOR,
    "perform_region_import":Q_EXTRACTOR,
    "perform_model_import":Q_EXTRACTOR,
    "perform_video_segmentation":Q_EXTRACTOR,
    "perform_video_decode":Q_EXTRACTOR,
    "perform_frame_download": Q_EXTRACTOR,
    "perform_dataset_extraction":Q_EXTRACTOR,
    "perform_transformation":Q_EXTRACTOR,
    "perform_export":Q_EXTRACTOR,
    "perform_deletion":Q_EXTRACTOR,
    "perform_sync":Q_EXTRACTOR,
    "perform_import":Q_EXTRACTOR,
    "perform_stream_capture": Q_STREAMER,
    "perform_matching": Q_TRAINER,
    "perform_training": Q_TRAINER,
    "perform_reduce": Q_REDUCER,
    "perform_video_decode_lambda": Q_LAMBDA
}

RESTARTABLE_TASKS = {'perform_video_segmentation', 'perform_indexing', 'perform_detection', 'perform_analysis',
                     'perform_frame_download', 'perform_video_decode', 'perform_test'}

NON_PROCESSING_TASKS = {'perform_training','perform_training_set_creation','perform_deletion', 'perform_export'}

TRAINING_TASKS = {'perform_training','perform_training_set_creation'}

# Is the code running on kubernetes?
KUBE_MODE = 'KUBE_MODE' in os.environ
# How many video segments should we process at a time?
DEFAULT_SEGMENTS_BATCH_SIZE = int(os.environ.get('DEFAULT_SEGMENTS_BATCH_SIZE',10))
# How many frames/images in a dataset should we process at a time?
DEFAULT_FRAMES_BATCH_SIZE = int(os.environ.get('DEFAULT_FRAMES_BATCH_SIZE',500))
# Default video decoding 1 frame per 30 frames AND all i-frames
DEFAULT_RATE = int(os.environ.get('DEFAULT_RATE',30))
# Max task attempts
MAX_TASK_ATTEMPTS = 5
# FAISS
ENABLE_FAISS = 'DISABLE_FAISS' not in os.environ
# Serializer version
SERIALIZER_VERSION = "0.1"

