#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess
import sys
from platform import system as system_type
from tkinter import Tk, messagebox

from win32api import GetLastError
from win32event import CreateMutex
from winerror import ERROR_ALREADY_EXISTS

import network_manager
import rwjson

# 使编译器能正确导入ico文件
if getattr(sys, 'frozen', None):
    basedir = sys._MEIPASS
else:
    basedir = os.path.dirname(__file__)

win = Tk()
win.withdraw()  # 禁用tkinter主窗口
# 如果正确导入了ico文件则设置tkinter对话框图标
if os.path.exists(os.path.join(basedir, "wangluo.ico")):
    win.iconbitmap(os.path.join(basedir, "wangluo.ico"))


# 目前未联网，尝试联网
def not_connected():
    print('目前状态：未联网\n尝试联网...')
    status = network_manager.connect_network()
    if status['result'] == 'success' and status['message'] == '':
        print('联网成功！')  # 控制台输出状态信息
        messagebox.showinfo(title='网络已连接', message='联网成功！')
    elif status['result'] == 'success' and status['message'] != '':
        print('校园网已连接:' + status['message'])
        messagebox.showinfo(title='网络已连接', message=status['message'])
    elif status['result'] == 'fail':
        error_message1 = '联网失败！\n失败原因：' + status['message']
        print(error_message1)  # 控制台输出错误信息
        messagebox.showerror(title='联网失败', message=error_message1)
    elif status['result'] != 'success' and status['result'] != 'fail':
        error_message2 = '未知错误：' + str(status)
        print(error_message2)
        messagebox.showerror(title='错误', message=error_message2)
    print(status)
    sys.exit(0)


# 目前已联网，询问是否需要断网
def connected():
    print('目前状态：已联网')
    f = rwjson.read_json()
    if f[0]['enable_disconnect']:
        print('询问是否需要断网')
        yesno1 = messagebox.askyesno(title='网络已连接', message='设备目前已联网，是否需要断网？', icon='info')
        if yesno1:
            print('用户选择断网，尝试断网...')
            status = network_manager.disconnect_network()
            if status['result'] == 'success':
                print('断网成功！')
                messagebox.showinfo(title='已断网', message='断网成功！')
            elif status['result'] == 'fail':
                error_message1 = '断网失败！\n失败原因：' + status['message']
                print(error_message1)
                messagebox.showerror(title='断网失败', message=error_message1)
            else:
                error_message2 = '未知错误：' + str(status)
                print(error_message2)
                messagebox.showerror(title='错误', message=error_message2)
            print(status)
        else:
            print('用户选择不断网，程序自动退出')
        sys.exit(0)
    else:
        print('配置文件未启用"enable_disconnect"，程序自动退出')
        sys.exit(0)


def main(system):
    # 先判断网络通断再执行操作
    # noinspection PyBroadException
    try:
        if system == 'Windows':
            print('系统类型：' + system)
            result = os.system(u'ping 119.29.29.29 -n 1 -w 1500')
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE  # default
            CREATE_NO_WINDOW = 0x08000000
            DETACHED_PROCESS = 0x00000008
            subprocess.call('taskkill /F /IM exename.exe', startupinfo=si, creationflags=DETACHED_PROCESS, shell=False)
        else:
            print('系统类型：' + system)
            result = os.system(u'ping 119.29.29.29 -c 1 -W 1500')
        if result == 0:
            connected()
        else:
            not_connected()
    except Exception as e:
        print('出现未知错误：', e)
        error_message = '出现未知错误，无法判断网络通断情况！\n是否要尝试联网？\n错误信息：' + str(e)
        yesno = messagebox.askyesno(title='未知错误', message=error_message, icon='error')
        if yesno:
            print('用户选择联网')
            not_connected()
        else:
            print('用户选择不联网，程序自动退出')
            sys.exit(1)


if __name__ == '__main__':
    print('判断系统类型...')
    system1 = system_type()
    if system1 == 'Windows':
        mutex_name = 'school_network'
        mutex = CreateMutex(None, False, mutex_name)
        if GetLastError() == ERROR_ALREADY_EXISTS:
            print('本程序不能同时运行多个实例，请不要多开')
            messagebox.showerror(title='警告', message='本程序不能同时运行多个实例，请不要多开')
            sys.exit(0)
        else:
            print('程序启动中...')
            main(system1)
    else:
        print('程序启动中...')
        main(system1)
