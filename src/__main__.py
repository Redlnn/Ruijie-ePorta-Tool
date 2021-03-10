#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys
from urllib.request import urlopen
from os import path, system
from platform import system as os_type
from platform import win32_ver
from tkinter import messagebox, Tk

from win10toast import ToastNotifier
from win32api import GetLastError
from win32event import CreateMutex
from winerror import ERROR_ALREADY_EXISTS

import config
import network_manager

# 使 pyinstaller 能正确导入ico文件
if getattr(sys, 'frozen', None):
    basedir = sys._MEIPASS  # noqa
else:
    basedir = path.dirname(__file__)

win = Tk()
win.withdraw()  # 禁用tkinter主窗口
toast = ToastNotifier()
windows_ver = win32_ver()

# 如果正确导入了ico文件则设置tkinter对话框与win10 toast的图标
if path.exists(path.join(basedir, 'wangluo.ico')):
    win.iconbitmap(path.join(basedir, 'wangluo.ico'))
    icon_path = path.join(basedir, 'wangluo.ico')


def connect(host='https://www.baidu.com', timeout=0.5) -> bool:
    try:
        urlopen(host, timeout=timeout)  # Python 3.x
        return True
    except:  # noqa
        return False


# 目前未联网，尝试联网
def disconnected(system_type):
    # 目前状态：未联网
    status = network_manager.connect_network()
    if status['result'] == 'success' and status['message'] == '':
        if system_type == 'Windows' and windows_ver[0] == '10':
            toast.show_toast(title='联网成功', msg='网络已连接！', icon_path=icon_path, duration=6, threaded=True)
        else:
            messagebox.showinfo(title='网络已连接', message='联网成功！')
    elif status['result'] == 'success' and status['message'] != '':
        if system_type == 'Windows' and windows_ver[0] == '10':
            toast.show_toast(title='联网成功', msg=status['message'], icon_path=icon_path, duration=10, threaded=True)
        else:
            messagebox.showinfo(title='网络已连接', message=status['message'])
    elif status['result'] == 'fail':
        error_message1 = '联网失败！\n失败原因：' + status['message']
        messagebox.showerror(title='联网失败', message=error_message1)
    elif status['result'] != 'success' and status['result'] != 'fail':
        error_message2 = '未知错误：' + str(status)
        messagebox.showerror(title='错误', message=error_message2)
    # print('返回值：', status)
    sys.exit(0)


# 目前已联网，询问是否需要断网
def connected(system_type):
    # 目前状态：已联网
    # 询问是否需要断网
    yesno1 = messagebox.askyesno(title='网络已连接', message='设备目前已联网，是否需要断网？', icon='info')
    if yesno1:
        # 用户选择断网，尝试断网
        status = network_manager.disconnect_network()
        if status['result'] == 'success':
            if system_type == 'Windows' and windows_ver[0] == '10':
                toast.show_toast(title='已断网', msg='断网成功！', icon_path=icon_path, duration=5)
            else:
                messagebox.showinfo(title='已断网', message='断网成功！')
        elif status['result'] == 'fail':
            error_message1 = '断网失败！\n失败原因：' + status['message']
            messagebox.showerror(title='断网失败', message=error_message1)
        else:
            error_message2 = '未知错误：' + str(status)
            messagebox.showerror(title='错误', message=error_message2)
        # print('返回值：', status)
    # 用户选择不断网，程序自动退出
    sys.exit(0)


def main(system_type):
    # 先判断网络通断再执行操作
    # noinspection PyBroadException
    f = config.read_json()
    if f['config']['enable_disconnect']:
        if connect():
            connected(system_type)
        else:
            if f['config']['allow_ping']:
                if not connect(host=f'http://{f["config"]["server"]}', timeout=0.3):
                    if system_type == 'Windows' and windows_ver[0] == '10':
                        toast.show_toast(title='网络环境错误', msg='当前不在校园网环境，不自动尝试连接校园网')
                    else:
                        messagebox.showinfo(title='网络环境错误', message='当前不在校园网环境，不自动尝试连接校园网')
                    sys.exit(0)
                else:
                    disconnected(system_type)
            else:
                disconnected(system_type)
    else:
        # 配置文件未启用"enable_disconnect"，程序将始终当作设备未联网
        disconnected(system_type)


if __name__ == '__main__':
    # 判断系统类型
    try:
        sys_type = os_type()
        if sys_type == 'Windows':
            # 检测多开
            mutex_name = 'school_network'
            mutex = CreateMutex(None, False, mutex_name)
            if GetLastError() == ERROR_ALREADY_EXISTS:
                messagebox.showerror(title='警告', message='本程序不能同时运行多个实例，请不要多开。\n若右下角仍有本程序通知，请关掉通知后重试！')
                sys.exit(0)
            else:
                main(sys_type)
        else:
            # 系统不是Windows，直接启动（没有Linux环境也懒得搞）
            main(sys_type)
    except KeyboardInterrupt:
        sys.exit()
