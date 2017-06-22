import urllib
from urllib import request, parse

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/55.0.2883.87 Safari/537.36',
    'contentType': 'utf-8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': 1,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
}

HTML_ENCODE = 'gbk'


# 发出带参数的get请求
def http_request_get_with_params(url_raw, params):
    url_params = parse.urlencode(params)
    url = url_raw + '?' + url_params
    return http_request_get(url)


# 根据url发出get请求
def http_request_get(url, addition_headers=None):
    req = request.Request(url, headers=HEADERS, method='GET')

    if addition_headers is not None:
        for k, v in addition_headers.items():
            req.add_header(k, v)

    response = urllib.request.urlopen(req)
    resp = response.read()
    return resp


# 根据url发出get请求
def http_request_post(url, params, addition_headers=None):
    data = parse.urlencode(params).encode(HTML_ENCODE)
    req = request.Request(url, headers=HEADERS, data=data, method='POST')

    if addition_headers is not None:
        for k, v in addition_headers.items():
            req.add_header(k, v)

    response = urllib.request.urlopen(req)
    resp = response.read()
    return resp
