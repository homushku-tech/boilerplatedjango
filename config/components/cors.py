from corsheaders.defaults import default_headers

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_HEADERS = (
        *default_headers,
        'Access-Control-Allow-Headers',
        'Access-Control-Allow-Credentials',
    )