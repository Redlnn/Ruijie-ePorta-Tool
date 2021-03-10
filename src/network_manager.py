#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from json import loads as json_loads
from os import path
from tkinter import messagebox, Tk

from requests import post

import config

# 使编译器能正确导入ico文件
if getattr(sys, 'frozen', None):
    basedir = sys._MEIPASS  # noqa
else:
    basedir = path.dirname(__file__)

win = Tk()
win.withdraw()  # 禁用tkinter主窗口
# 如果正确导入了ico文件则设置tkinter对话框图标
if path.exists(path.join(basedir, 'wangluo.ico')):
    win.iconbitmap(path.join(basedir, 'wangluo.ico'))


def connect_network():
    f = config.read_json()
    url = f['server']['login_url']
    data = f['login_data']
    header = f['login_header']
    cookie = f['cookie']

    try:
        res = post(url=url, data=data, headers=header, cookies=cookie)
    except Exception as e:
        error_message = '出现错误！\n\n错误信息：' + str(e)
        messagebox.showerror(title='未知错误', message=error_message)
        sys.exit(1)
    else:
        res.encoding = 'utf-8'
        json1 = json_loads(res.text)
        return json1


def disconnect_network():
    f = config.read_json()
    url = f['server']['logout_url']
    data = f['logout_data']
    header = f['logout_header']

    try:
        res = post(url=url, data=data, headers=header)
    except Exception as e:
        error_message = '出现错误！\n\n错误信息：' + str(e)
        messagebox.showerror(title='未知错误', message=error_message)
        sys.exit(1)
    else:
        res.encoding = 'utf-8'
        json1 = json_loads(res.text)
        return json1
