from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────
# 보안
# ──────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-this-in-production")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# ──────────────────────────────────────────
# 앱
# ──────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 서드파티
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    # 내부
    "core",
    "accounts",
]

# ──────────────────────────────────────────
# 미들웨어
# ──────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",          # CORS — 반드시 CommonMiddleware 위에
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ──────────────────────────────────────────
# DB (PostgreSQL / 개발 중 SQLite 폴백)
# ──────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "")

if DATABASE_URL:
    # PostgreSQL: DATABASE_URL=postgres://user:pass@localhost:5432/buildsafe
    import urllib.parse as up
    r = up.urlparse(DATABASE_URL)
    DATABASES = {
        "default": {
            "ENGINE":   "django.db.backends.postgresql",
            "NAME":     r.path.lstrip("/"),
            "USER":     r.username,
            "PASSWORD": r.password,
            "HOST":     r.hostname,
            "PORT":     r.port or 5432,
        }
    }
else:
    # 로컬 개발: SQLite (PostgreSQL 세팅 전 빠르게 돌릴 때)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME":   BASE_DIR / "db.sqlite3",
        }
    }

# ──────────────────────────────────────────
# DRF 설정
# ──────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# ──────────────────────────────────────────
# CORS (Vue 개발 서버 허용)
# ──────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",   # Vite 기본 포트
    "http://localhost:5174",   # PaceFlow 프론트 개발 포트
    "http://localhost:5175",   # 포트 충돌 시 Vite 대체 포트
    "http://localhost:5176",   # 로컬 API 연동 확인용 대체 포트
    "http://localhost:3000",
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://localhost:\d+$",
    r"^http://127\.0\.0\.1:\d+$",
]
CORS_ALLOW_CREDENTIALS = True

# ──────────────────────────────────────────
# 외부 API 키
# ──────────────────────────────────────────
NARAJANGTEO_API_KEY      = os.getenv("NARAJANGTEO_API_KEY", "")
NARAJANGTEO_USER_API_KEY = os.getenv("NARAJANGTEO_USER_API_KEY", "")  # 추가
JUSO_API_KEY             = os.getenv("JUSO_SEARCH_API_KEY", os.getenv("JUSO_API_KEY", ""))
KAKAO_REST_API_KEY       = os.getenv("KAKAO_REST_API_KEY", "")
KAKAO_MAP_KEY            = os.getenv("KAKAO_MAP_KEY", "")

# ──────────────────────────────────────────
# 국제화
# ──────────────────────────────────────────
LANGUAGE_CODE = "ko-kr"
TIME_ZONE     = "Asia/Seoul"
USE_I18N      = True
USE_TZ        = True

# ──────────────────────────────────────────
# 정적 파일
# ──────────────────────────────────────────
STATIC_URL  = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
