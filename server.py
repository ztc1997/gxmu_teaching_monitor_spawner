import binascii
import http.cookiejar
import os
import time
import urllib.request

from flask import Flask, render_template, make_response
from flask_socketio import SocketIO, emit

import academic as academic_tool
import dqzljk as dqzljk_tool

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

max_age = 24 * 60 * 60


@app.route('/')
def root():
    return render_template('index.html', activated_item='root')


academic_users = set()


@app.route('/academic', methods=['GET', 'POST'])
def academic():
    resp = make_response(
        render_template('academic.html', activated_item='academic'))
    return resp


@socketio.on('spawn', namespace='/academic')
def academic_task(data):
    username = data['username']
    password = data['password']

    if not username or not password:
        emit('update', '请填入用户名和密码')
        emit('complete')
        return

    if username in academic_users:
        emit('update', '任务进行中')
        emit('complete')
        return

    academic_users.add(username)
    http_handler = urllib.request.HTTPHandler(debuglevel=0)
    # cookie处理器
    cj = http.cookiejar.LWPCookieJar()
    cookie_support = urllib.request.HTTPCookieProcessor(cj)
    opener = urllib.request.build_opener(cookie_support, http_handler)

    try:
        emit('update', '正在登录')
        academic_tool.login(username, password, opener=opener)
    except Exception as e:
        emit('update', '登录失败')
        emit('complete')
        academic_users.remove(username)
        log('academic: ' + '%s %s 登录失败  %s' % (
            time.asctime(time.localtime(time.time())), username, e.args))
        return

    count = 0

    try:
        emit('update', '正在获取任务列表')
        infolist = academic_tool.teaching_evaluate_list(opener)
        for info in infolist:
            status_halt = info.find(class_='statushalt')
            if status_halt is not None:
                emit('update', ('正在评教：%s' % info.td.string))
                url = info.find(text='评估').parent['href'].replace('.', 'eva/index', 1)
                academic_tool.teaching_evaluate(url, opener)
                count += 1
    except Exception as e:
        emit('update', '登录成功，但发生其他错误')
        emit('complete')
        academic_users.remove(username)
        log('academic: ' + '%s %s 登录成功，但发生其他错误 %s' % (
            time.asctime(time.localtime(time.time())), username, e.args))
        return

    emit('update', '评教完成，共%d个' % count)
    emit('complete')
    academic_users.remove(username)
    log('academic: ' + '%s %s 评教成功' % (time.asctime(time.localtime(time.time())), username))


dqzljk_users = set()


@app.route('/dqzljk', methods=['get', 'post'])
def dqzljk():
    resp = make_response(
        render_template('dqzljk.html', activated_item='dqzljk'))
    return resp


@socketio.on('spawn', namespace='/dqzljk')
def dqzljk_task(data):
    username = data['username']
    password = data['password']

    if not username or not password:
        emit('update', '请填入用户名和密码')
        emit('complete')
        return

    if username in dqzljk_users:
        emit('update', '任务进行中')
        emit('complete')
        return
    dqzljk_users.add(username)

    http_handler = urllib.request.HTTPHandler(debuglevel=0)
    # cookie处理器
    cj = http.cookiejar.LWPCookieJar()
    cookie_support = urllib.request.HTTPCookieProcessor(cj)
    opener = urllib.request.build_opener(cookie_support, http_handler)

    try:
        emit('update', '正在登录')
        dqzljk_tool.login(username, password, opener)
    except Exception as e:
        emit('update', '登录失败')
        emit('complete')
        dqzljk_users.remove(username)
        log('dqzljk: ' + '%s %s 登录失败  %s' % (
            time.asctime(time.localtime(time.time())), username, e.args))
        return

    count = 0

    try:
        emit('正在获取任务列表')
        tasks = dqzljk_tool.obtain_teaching_evaluate_tasks(opener)
        for i, task in enumerate(tasks):
            emit('正在评教，第 %d 个\t/\t共 %d 个' % (i + 1, len(tasks)))
            dqzljk_tool.teaching_evaluate(task, opener)
            count += 1
    except Exception as e:
        emit('update', '登录成功，但发生其他错误')
        emit('complete')
        dqzljk_users.remove(username)
        log('dqzljk: ' + '%s %s 登录成功，但发生其他错误 %s' % (
            time.asctime(time.localtime(time.time())), username, e.args))
        return

    emit('update', '评教完成，共%d个' % count)
    emit('complete')
    dqzljk_users.remove(username)
    log('dqzljk: ' + '%s %s 评教成功' % (time.asctime(time.localtime(time.time())), username))


def generate_token():
    return str(binascii.b2a_base64(os.urandom(24))[:-1])


def log(text):
    output = open('log.txt', 'a', encoding="utf-8")
    try:
        output.write(text + '\n')
    finally:
        output.close()


if __name__ == '__main__':
    socketio.run(app)
