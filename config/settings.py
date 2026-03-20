from pathlib import Path
import os
import environ
import sys

# 1. 환경변수
env = environ.Env(
    DEBUG=(bool, False)
)
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
db_mode = env('DB_MODE', default='sqlite')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# 2. 앱 설정 (DRF, SimpleJWT 제거)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party
    'corsheaders', # CORS는 필수

    # Local Apps
    'common',
    'posts',
    'uploads',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # 최상단
    'django.middleware.security.SecurityMiddleware',
    'common.middleware.AutoBanMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'config.wsgi.application'

# 3. 데이터베이스 (MariaDB)
if db_mode == 'sqlite':
    DATABASES = {
        'default' : {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    db_ssl_ca = env("DB_SSL_CA", default="/etc/ssl/certs/ca-certificates.crt")
    db_use_ssl = env.bool("DB_USE_SSL", default=True)
    mysql_options = {"charset": "utf8mb4"}
    if db_use_ssl:
        mysql_options["ssl"] = {"ca": db_ssl_ca}

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ["DB_NAME_POSTS"],
            "USER": os.environ["DB_USER_POSTS"],
            "PASSWORD": os.environ["DB_PASSWORD_POSTS"],
            "HOST": os.environ["DB_HOST"],
            "PORT": "3306",
            "OPTIONS": mysql_options,
        }
    }

# 4. 비밀번호 검증
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 5. 언어 및 시간
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

# 6. Trailing Slash 제거
APPEND_SLASH = False

# 7. CORS 설정
CORS_ALLOW_ALL_ORIGINS = DEBUG
if not DEBUG:
    CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

# 7-1. Internal API routing (service-to-service)
USE_INTERNAL_SERVICE_API = env.bool("USE_INTERNAL_SERVICE_API", default=False)
AUTH_INTERNAL_BASE_URL = env("AUTH_INTERNAL_BASE_URL", default="")
EVENTS_INTERNAL_BASE_URL = env("EVENTS_INTERNAL_BASE_URL", default="")
POSTS_INTERNAL_BASE_URL = env("POSTS_INTERNAL_BASE_URL", default="")

# 7-2. API Gateway auth handoff
GATEWAY_USER_ID_HEADER = env("GATEWAY_USER_ID_HEADER", default="X-User-Id")

# 9. 정적파일경로설정
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# 10. ALB사용 시 리다이렉션 오류 방지
# ALB가 전달해준 원래 호스트 정보를 신뢰합니다.
USE_X_FORWARDED_HOST = True


# 11. AWS S3 (Presigned Upload)
AWS_REGION = env("AWS_REGION", default=env("AWS_DEFAULT_REGION", default="ap-northeast-2"))

# 11-1. bucket 키는 여러 이름 fallback 지원
S3_UPLOAD_BUCKET = env(
    "S3_UPLOAD_BUCKET",
    default=env("AWS_STORAGE_BUCKET_NAME", default=env("S3_BUCKET", default="")),
)
S3_UPLOAD_PREFIX = env("S3_UPLOAD_PREFIX", default="uploads/")
S3_PRESIGN_EXPIRES = env.int("S3_PRESIGN_EXPIRES", default=300)
S3_PUBLIC_BASE_URL = env("S3_PUBLIC_BASE_URL", default=None)

# 12. Notification
NOTIFICATION_EVENT_BUS_NAME = env("NOTIFICATION_EVENT_BUS_NAME", default="stagelog-notification-bus")

# 13. Redis (ElastiCache)
REDIS_HOST = env("REDIS_HOST", default="")
REDIS_PORT = env.int("REDIS_PORT", default=6379)
REDIS_DB = env.int("REDIS_DB", default=0)
REDIS_PASSWORD = env("REDIS_PASSWORD", default="")
REDIS_SSL = env.bool("REDIS_SSL", default=False)

# 14. Auto Ban (IP filter)
AUTO_BAN_ENABLED = env.bool("AUTO_BAN_ENABLED", default=False)
AUTO_BAN_LIMIT_WINDOW_SECONDS = env.int("AUTO_BAN_LIMIT_WINDOW_SECONDS", default=60)
AUTO_BAN_MAX_REQUESTS = env.int("AUTO_BAN_MAX_REQUESTS", default=100)
AUTO_BAN_BLOCK_TIME_SECONDS = env.int("AUTO_BAN_BLOCK_TIME_SECONDS", default=3600)

# 15. Cache (Redis 공유 / 로컬 fallback)
if REDIS_HOST:
    redis_auth = ""
    if REDIS_PASSWORD:
        redis_auth = f":{REDIS_PASSWORD}@"
    redis_scheme = "rediss" if REDIS_SSL else "redis"
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": f"{redis_scheme}://{redis_auth}{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }
