from pathlib import Path
import os

import sentry_sdk


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')
SERVER_ENV = os.environ.get('SERVER_ENV')

if SERVER_ENV in ['Local', 'k8s']:
    DEBUG = True
    ALLOWED_HOSTS = ["*"]
else:
    DEBUG = os.environ.get('DJANGO_DEBUG') == 'True'
    ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS').split(',')

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
]

THIRD_APPS = [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.naver',
    'allauth.socialaccount.providers.kakao',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    'ckeditor',
    'ckeditor_uploader',
    'django_crontab',
    'django_celery_results',
    'debug_toolbar',
    'constance',
    'django_elasticsearch_dsl',
]

PROJECT_APPS = [
    'accounts.apps.AccountsConfig',
    'notification.apps.NotificationConfig',
    'board',
    'control',
    'chatgpt',
    'common',
    'popup',
]

PROJECT_SETTING_APPS = [
    'django_seed',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_APPS + PROJECT_APPS + PROJECT_SETTING_APPS

CKEDITOR_UPLOAD_PATH = "post-body/"

CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_YourCustomToolbarConfig': [
            {'name': 'document', 'items': ['Source', '-', '-', 'Templates']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
                       'Language']},
            {'name': 'extra',
             'items': [
                 'CodeSnippet', ],
             },
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert',
             'items': ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
            {'name': 'about', 'items': ['About']},
            '/',  # put this to force next toolbar on new line
            {'name': 'yourcustomtools', 'items': [
                # put the name of your editor.ui.addButton here
                'Preview',
                'Maximize',
            ]},
        ],
        'toolbar': 'YourCustomToolbarConfig',  # put selected toolbar config here
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage',  # the upload image feature
            # your extra plugins here
            'codesnippet',
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            # 'devtools',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
    }
}

AUTH_USER_MODEL = 'accounts.User'

# SOCIAL 로그인 관련
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = 1

LOGIN_REDIRECT_URL = '/'

ACCOUNT_SIGNUP_REDIRECT_URL = '/'

ACCOUNT_UNIQUE_EMAIL = False

SOCIALACCOUNT_PROVIDER = {

}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'common.middlewares.visitor_count_middleware.VisitorCountMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'board.context_processors.nav_board',
                'control.context_processors.visitor_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

BACKUP_PATH = os.environ.get('BACKUP_PATH')

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = False

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'temp_static')
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'file': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'app.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,  # 5 개 로테이션
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

NOTICE_EMAILS = [os.environ.get('NOTICE_EMAILS')]

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_USE_TLS = True

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = int(os.environ.get('REDIS_PORT'))
REDIS_DB = int(os.environ.get('REDIS_DB'))

# CELERY SETTINGS
timezone = 'Asia/Seoul'
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
result_backend = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
accept_content = ["json"]
task_serializer = "json"
result_serializer = "json"

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

CHATGPT_KEY = os.environ.get('CHATGPT_KEY')

INTERNAL_IPS = [
    '127.0.0.1',
]

WEB_HOOK_ADDRESS = os.environ.get('WEB_HOOK_ADDRESS')


CONSTANCE_IGNORE_ADMIN_VERSION_CHECK = True
CONSTANCE_FILE_ROOT = 'constance'

CONSTANCE_ADDITIONAL_FIELDS = {
    'image_field': ['django.forms.ImageField', {}]
}

CONSTANCE_REDIS_CONNECTION = {
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'db': REDIS_DB,
}

CONSTANCE_CONFIG = {
    'PROFILE_DESCRIPTION_MARKDOWN': (
        '',
        '홈 화면에 보이는 자기 소개 MARKDOWN 부분',
    ),
    'PROFILE_IMAGE_URL': (
        '',
        '홈 화면에 보이는 자기 소개 프로필 사진 URL',
        'image_field',
    ),
    'PROFILE_NAME': (
        '',
        '홈 화면에 보이는 이름',
    ),
    'PROFILE_SIMPLE_DESCRIPTION': (
        '',
        '홈 화면에 보이는 간단 소개',
    ),
}

if SERVER_ENV == 'K8s':
    # Kubernetes 환경에서는 마운트된 파일 경로 사용
    GOOGLE_SERVICE_ACCOUNT_FILE = '/app/secrets/google_service_account_file.json'
else:
    # 로컬 개발 환경에서는 기존 경로 사용
    GOOGLE_SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'google_service_account_file.json')

GOOGLE_API_SCOPES = [
    'https://www.googleapis.com/auth/drive',
]
GOOGLE_DRIVE_MEDIA_BACKUP_FOLDER_ID = os.environ.get('GOOGLE_DRIVE_MEDIA_BACKUP_FOLDER_ID')

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': [
            {
                'host': os.environ.get('ELASTICSEARCH_HOST'),
                'port': os.environ.get('ELASTICSEARCH_PORT'),
                'use_ssl': True,
                'ca_certs': os.path.join(BASE_DIR, 'http_ca.crt'),
            }
        ],
        'http_auth': (os.environ.get('ELASTICSEARCH_USERNAME'), os.environ.get('ELASTICSEARCH_PASSWORD')),
    },
}

if not DEBUG:
    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DNS'),
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        environment='production'
    )
