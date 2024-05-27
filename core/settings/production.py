from .base import *  # noqa

###################################################################
# General
###################################################################

DEBUG = True

###################################################################
# Django security
###################################################################

# USE_X_FORWARDED_HOST = True
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

ENV_TRUSTED_ORIGINS = env.list("TRUSTED_ORIGINS", default=[])  # noqa

CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = [
    "http://*",
    *ENV_TRUSTED_ORIGINS,
]

###################################################################
# CORS
###################################################################

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ["*"]
