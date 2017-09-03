#!/usr/bin/env python3
# encoding: utf-8
# -*- coding=utf-8 -*-
import getpass
import http.cookiejar
import json
import socket
import urllib
from urllib import request, parse

from bs4 import BeautifulSoup as Soup

import http_tool

__doc__ = '广西医科大学教学质量实时监控系统，刷评教工具'

BEAUTIFUL_SOUP_FEATURES = 'html5lib'

URL_BASE = 'http://210.36.49.12/dqzljk/'

http_handler = request.HTTPHandler(debuglevel=0)
# cookie处理器
cj = http.cookiejar.LWPCookieJar()
cookie_support = request.HTTPCookieProcessor(cj)
my_opener = request.build_opener(cookie_support, http_handler)
socket.setdefaulttimeout(5)


def login(username, password, opener=my_opener):
    # resp = http_request_get('doLogin.do')
    # soup = Soup(resp, BEAUTIFUL_SOUP_FEATURES)
    # print(soup)
    data = {'forward': '${forward?if_exists}', 'loginType': 2, 'uname': username, 'pwd': password, 'Submit': '登录系统'}
    resp = http_tool.http_request_post(URL_BASE + 'doLogin.do', data, opener)
    soup = Soup(resp, BEAUTIFUL_SOUP_FEATURES)
    if soup.title.string == '操作失败':
        err = soup.select('td[align="left"]')[1].string
        raise Exception(err)


def obtain_teaching_evaluate_tasks(opener=my_opener):
    resp = http_tool.http_request_get(URL_BASE + 'stuMission.do', opener)
    soup = Soup(resp, BEAUTIFUL_SOUP_FEATURES)
    datatable = soup.select('#datatable')[1].tbody.contents[2::2]
    tasks = []
    for data in datatable:
        a = data.contents[9].contents[1].a
        if a is None:
            continue
        task = urllib.parse.quote(a['href'], safe='?=&')
        tasks.append(task)
    return tasks


def teaching_evaluate(url, opener=my_opener):
    url_params = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)

    resp = http_tool.http_request_get(URL_BASE + url, opener, {'Referer': 'http://210.36.49.12/dqzljk/stuMission.do'})
    soup = Soup(resp, BEAUTIFUL_SOUP_FEATURES)
    token_str = soup.select('#tokenStr')[0]['value']

    resp = http_tool.http_request_post(URL_BASE + 'getGread.do?', opener, {'contentId': url_params['tcid'][0]},
                                       {'Referer': URL_BASE + url})
    gread = json.loads(resp.decode("utf-8").split('p~p')[4].replace('\'', '\"'))[1:]

    mark_str = ''
    standard_id = ''
    for item in gread:
        standard_id += item['id'] + '~'
        mark_str += '4~'

    post_params = {'tokenStr': token_str, 'skid': url_params['skid'][0], 'standardid': standard_id, 'markStr': mark_str,
                   'comment': '--------请在这里填写您的建议--------', 'totalMark': 80, 'gmodel': 1,
                   'courseid': url_params['courseid'][0], 'cname': url_params['cname'][0],
                   'teacherid': url_params['teacherid'][0], 'tname': url_params['tname'][0],
                   'ctid': url_params['contentid'][0],
                   'ctype': 1}
    resp = http_tool.http_request_post(URL_BASE + 'stuPgAjax.do?', post_params, opener, {'Referer': URL_BASE + url})


if __name__ == '__main__':
    username = input('输入用户名：')
    password = getpass.getpass('输入密码（输入不会显示）：')
    login(username, password)
    print('正在获取任务列表')
    tasks = obtain_teaching_evaluate_tasks()
    for i, task in enumerate(tasks):
        print('第 %d 个\t/\t共 %d 个' % (i + 1, len(tasks)))
        teaching_evaluate(task)
