
# helpful reused variables
HTTP_TOO_MANY_REQUESTS = 429
HTTP_BAD_REQUEST = 400


def get_api_key(platform="alma", api="bibs", env="sandbox"):
    return API_KEYS[platform][api][env]
