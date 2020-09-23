#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys
from json import dump as json_dump
from json import load as json_load
from os import system, path
from platform import system as os_type
from tkinter import Tk, messagebox

# 使编译器能正确导入ico文件
if getattr(sys, 'frozen', None):
    basedir = sys._MEIPASS
else:
    basedir = path.dirname(__file__)

win = Tk()
win.withdraw()  # 禁用tkinter主窗口
# 如果正确导入了ico文件则设置tkinter对话框图标
if path.exists(path.join(basedir, "wangluo.ico")):
    win.iconbitmap(path.join(basedir, "wangluo.ico"))


# 写入配置文件
def write_json():
    # 登录与登出的目标url及主程序是否需要检测校园网环境
    url = {
        '警告1': '请不要增删本配置文件中的任何条目或改动顺序',
        '警告2': '请按照模板填写本配置文件',
        '提示': '本配置文件内容应来自于抓包，不排除将来可能会失效',
        'allow_ping指校园网登录服务器是否允许ping': '根据下面server项的值ping',
        'login_url为登录时传参的地址': 'logout_url为下线时传参的地址',
        'enable_disconnect用于控制在网络已连接时运行脚本是否提示断网': '',
        'allow_ping': True,
        'server': '127.0.0.1',
        'login_url': 'http://127.0.0.1/eportal/InterFace.do?method=login',
        'logout_url': 'http://127.0.0.1/eportal/InterFace.do?method=logout',
        'enable_disconnect': True
    }
    # 登录传入参数
    login_data = {
        'userId': '00000000000',
        'password': '',
        'service': '',
        'queryString': '',
        'operatorPwd': '',
        'operatorUserId': '',
        'validcode': '',
        'passwordEncrypt': ''
    }
    # 断线传入参数
    logout_data = {
        'userIndex': '',
    }
    # 登录HTML Header
    login_header = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Connection': 'keep-alive',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': '',
    }
    # 断线HTML Header
    logout_header = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Connection': 'keep-alive',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': '',
    }

    cookie = {
        'EPORTAL_COOKIE_SAVEPASSWORD': 'tre',
        'EPORTAL_AUTO_LAND': '',
        'EPORTAL_COOKIE_USERNAME': '',
        'EPORTAL_COOKIE_OPERATORPWD': '',
        'EPORTAL_COOKIE_DOMAIN': '',
        'EPORTAL_COOKIE_PASSWORD': ''
    }

    # 构造json文本
    all_json = [url, login_data, logout_data, login_header, logout_header, cookie]
    # noinspection PyBroadException
    try:
        with open('./config.json', 'w', encoding='utf-8') as f:
            json_dump(all_json, f, ensure_ascii=False, indent=4, allow_nan=False)
        f.close()
    except Exception as e:
        error_message = '尝试写入新配置文件时出错\n' + str(e)
        messagebox.showerror(title='错误', message=error_message)
        sys.exit(1)


def check_school_net(h):
    if os_type() == 'Windows':
        result = system(u'ping ' + h[0]['server'] + u' -n 1 -w 50')
        # CREATE_NO_WINDOW = 0x08000000
        DETACHED_PROCESS = 0x00000008
        subprocess.call('taskkill /F /IM exename.exe', creationflags=DETACHED_PROCESS, shell=False)
    else:
        result = system(u'ping ' + h[0]['server'] + u' -c 1 -W 50')

    if result == 0:
        return 1
    else:
        messagebox.showwarning(title='警告', message='当前不在校园网环境，程序自动退出！')
        sys.exit(0)


def read_json():
    try:
        f = open('./config.json', mode='r', encoding='utf-8')
    except IOError:
        write_json()
        messagebox.showwarning(title='警告', message='配置文件不存在，已生成新配置文件，请填写配置文件后重试!')
        sys.exit(1)
    else:
        h = json_load(f)
        # 读取配置文件
        f.close()
        if h[0]['login_url'] == 'http://127.0.0.1/eportal/InterFace.do?method=login' \
                or h[0]['logout_url'] == 'http://127.0.0.1/eportal/InterFace.do?method=logout':
            messagebox.showwarning(title='警告', message='配置文件未填写完整，请填写配置文件后重试!')
            sys.exit(1)
        if h[0]['allow_ping']:
            if check_school_net(h) == 1:
                return h
        else:
            return h
