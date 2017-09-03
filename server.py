import binascii
import os
import _thread

import time

import academic as academic_tool
import dqzljk as dqzljk_tool
import http.cookiejar
import urllib.request

from flask import Flask, render_template, make_response, request, Response

app = Flask(__name__)

max_age = 24 * 60 * 60


@app.route('/')
def root():
    return render_template('index.html', activated_item='root')


tokens = {}
academic_users = set()


@app.route('/academic', methods=['GET', 'POST'])
def academic():
    set_cookie = False
    token = request.cookies.get('token', None)
    if token is None or token not in tokens:
        token = generate_token()
        set_cookie = True
    if request.method == 'POST':
        username = request.form['username']
        if username in academic_users:
            return '任务进行中'

        password = request.form['password']

        academic_users.add(username)
        _thread.start_new_thread(academic_task, (username, password, token))

        resp = Response('提交成功，稍后刷新页面查看结果')
        if set_cookie:
            resp.set_cookie('token', token, max_age=max_age)
            tokens[token] = {}
        return resp
    resp = make_response(
        render_template('academic.html', activated_item='academic', state=tokens.get(token, {}).get('academic', None)))
    if set_cookie:
        resp.set_cookie('token', token, max_age=max_age)
        tokens[token] = {}
    return resp


def academic_task(username, password, token):
    http_handler = urllib.request.HTTPHandler(debuglevel=0)
    # cookie处理器
    cj = http.cookiejar.LWPCookieJar()
    cookie_support = urllib.request.HTTPCookieProcessor(cj)
    opener = urllib.request.build_opener(cookie_support, http_handler)

    try:
        academic_tool.login(username, password, opener=opener)
    except Exception as e:
        tokens[token]['academic'] = '%s %s 登录失败  %s' % (
            time.asctime(time.localtime(time.time())), username, e.args)
        academic_users.remove(username)
        log('academic: ' + tokens[token]['academic'])
        return

    try:
        tokens[token]['academic'] = '正在评教'
        academic_tool.teaching_evaluate_all(opener=opener)
    except Exception as e:
        tokens[token]['academic'] = '%s %s 登录成功，但发生其他错误 %s' % (
            time.asctime(time.localtime(time.time())), username, e.args)
        academic_users.remove(username)
        log('academic: ' + tokens[token]['academic'])
        return

    tokens[token]['academic'] = '%s %s 评教成功' % (time.asctime(time.localtime(time.time())), username)
    academic_users.remove(username)
    log('academic: ' + tokens[token]['academic'])


dqzljk_users = set()


@app.route('/dqzljk', methods=['get', 'post'])
def dqzljk():
    set_cookie = False
    token = request.cookies.get('token', None)
    if token is None or token not in tokens:
        token = generate_token()
        set_cookie = True
    if request.method == 'POST':
        username = request.form['username']
        if username in dqzljk_users:
            return '任务进行中'

        password = request.form['password']

        dqzljk_users.add(username)
        _thread.start_new_thread(dqzljk_task, (username, password, token))

        resp = Response('提交成功，稍后刷新页面查看结果')
        if set_cookie:
            resp.set_cookie('token', token, max_age=max_age)
            tokens[token] = {}
        return resp
    resp = make_response(
        render_template('dqzljk.html', activated_item='dqzljk', state=tokens.get(token, {}).get('dqzljk', None)))
    if set_cookie:
        resp.set_cookie('token', token, max_age=max_age)
        tokens[token] = {}
    return resp


def dqzljk_task(username, password, token):
    http_handler = urllib.request.HTTPHandler(debuglevel=0)
    # cookie处理器
    cj = http.cookiejar.LWPCookieJar()
    cookie_support = urllib.request.HTTPCookieProcessor(cj)
    opener = urllib.request.build_opener(cookie_support, http_handler)

    try:
        dqzljk_tool.login(username, password, opener)
    except Exception as e:
        tokens[token]['dqzljk'] = '%s %s 登录失败  %s' % (
            time.asctime(time.localtime(time.time())), username, e.args)
        dqzljk_users.remove(username)
        log('dqzljk: ' + tokens[token]['dqzljk'])
        return

    try:
        tokens[token]['dqzljk'] = '正在获取任务列表'
        tasks = dqzljk_tool.obtain_teaching_evaluate_tasks(opener)
        for i, task in enumerate(tasks):
            tokens[token]['dqzljk'] = '正在评教，第 %d 个\t/\t共 %d 个' % (i + 1, len(tasks))
            dqzljk_tool.teaching_evaluate(task, opener)
    except Exception as e:
        tokens[token]['dqzljk'] = '%s %s 登录成功，但发生其他错误 %s' % (
            time.asctime(time.localtime(time.time())), username, e.args)
        dqzljk_users.remove(username)
        log('dqzljk: ' + tokens[token]['dqzljk'])
        return

    tokens[token]['dqzljk'] = '%s %s 评教成功' % (time.asctime(time.localtime(time.time())), username)
    dqzljk_users.remove(username)
    log('dqzljk: ' + tokens[token]['dqzljk'])


def generate_token():
    return str(binascii.b2a_base64(os.urandom(24))[:-1])


def log(text):
    output = open('log.txt', 'a', encoding="utf-8")
    try:
        output.write(text + '\n')
    finally:
        output.close()


if __name__ == '__main__':
    app.run()
