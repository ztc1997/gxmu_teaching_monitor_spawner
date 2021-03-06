from urllib import parse
from retrying import retry

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/55.0.2883.87 Safari/537.36',
    'contentType': 'utf-8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': 1,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
}

HTML_ENCODE = 'gbk'
REQUEST_TIMEOUT = 2


# 发出带参数的get请求
def http_request_get_with_params(url_raw, params, opener, addition_headers=None):
    url_params = parse.urlencode(params)
    url = url_raw + '?' + url_params
    return http_request_get(url, opener, addition_headers)


# 根据url发出get请求
def http_request_get(url, opener, addition_headers=None):
    set_opener_header(opener, addition_headers)

    return make_request(opener, url)


# 根据url发出get请求
def http_request_post(url, params, opener, addition_headers=None):
    data = parse.urlencode(params).encode(HTML_ENCODE)

    set_opener_header(opener, addition_headers)

    return make_request(opener, url, data)


def retry_if_timeout_error(exception):
    return isinstance(exception, TimeoutError)


@retry(stop_max_attempt_number=2, retry_on_exception=retry_if_timeout_error)
def make_request(opener, url, data=None):
    response = opener.open(url, data, timeout=REQUEST_TIMEOUT)
    resp = response.read()
    return resp


def set_opener_header(opener, addition_headers=None):
    opener.addheaders = HEADERS.items()
    if addition_headers is not None:
        opener.addheaders = list(opener.addheaders)
        for k, v in addition_headers.items():
            opener.addheaders.append((k, v))
