#!/usr/bin/env python3
# encoding: utf-8
# -*- coding=utf-8 -*-
import getpass
import http.cookiejar
import socket
from urllib import request

from bs4 import BeautifulSoup as Soup

import http_tool

__doc__ = '广西医科大学教务系统系统，刷评教工具'

HTML_ENCODE = 'gbk'

BEAUTIFUL_SOUP_FEATURES = 'html5lib'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/55.0.2883.87 Safari/537.36',
    'contentType': 'utf-8',
    'Connection': 'keep-alive'
}

URL_BASE = 'http://210.36.48.230/academic/'


def login(username, password):
    resp = http_tool.http_request_get(URL_BASE + 'index.jsp')
    # soup = Soup(resp, BEAUTIFUL_SOUP_FEATURES)
    # print(soup)
    data = {'j_username': username, 'j_password': password, 'button1': '登 录'}
    resp = http_tool.http_request_post(URL_BASE + 'j_acegi_security_check', data)
    # soup = Soup(resp, BEAUTIFUL_SOUP_FEATURES)
    # print(soup)


def teaching_evaluate_all():
    resp = http_tool.http_request_get(URL_BASE + 'accessModule.do?moduleId=508&groupId=')
    soup = Soup(resp, BEAUTIFUL_SOUP_FEATURES)
    infolist = soup.select('.infolist_common')
    # print(infolist)
    for info in infolist:
        status_halt = info.find(class_='statushalt')
        if status_halt is not None:
            url = info.find(text='评估').parent['href'].replace('.', 'eva/index', 1)
            print(url)
            teaching_evaluate(url)


def teaching_evaluate(url):
    resp = http_tool.http_request_get(URL_BASE + url)
    soup = Soup(resp, BEAUTIFUL_SOUP_FEATURES)
    inputs = soup.find_all(['input', 'textarea'])
    data = {}
    for i in inputs:
        if i.has_attr('type') and i['type'] == 'button':
            continue
        if i.name == 'textarea':
            i['value'] = '上课讲的很好'
        elif len(i['value']) == 0 and i['name'].startswith('itemid'):
            i['value'] = '95'
        data[i['name']] = i['value']
    resp = http_tool.http_request_post(URL_BASE + 'eva/index/putresult.jsdo', data)


http_handler = request.HTTPHandler(debuglevel=1)
# cookie处理器
cj = http.cookiejar.LWPCookieJar()
cookie_support = request.HTTPCookieProcessor(cj)
opener = request.build_opener(cookie_support, http_handler)
request.install_opener(opener)
socket.setdefaulttimeout(5)

if __name__ == '__main__':
    username = input('输入用户名：')
    password = getpass.getpass('输入密码（输入不会显示）：')
    login(username, password)
    teaching_evaluate_all()
