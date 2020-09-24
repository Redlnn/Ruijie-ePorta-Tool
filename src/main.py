#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys
from os import system, path
from platform import system as os_type
from platform import win32_ver
from tkinter import Tk, messagebox

from win10toast import ToastNotifier
from win32api import GetLastError
from win32event import CreateMutex
from winerror import ERROR_ALREADY_EXISTS

import network_manager
import rwjson

# 使编译器能正确导入ico文件
if getattr(sys, 'frozen', None):
    basedir = sys._MEIPASS
else:
    basedir = path.dirname(__file__)

win = Tk()
win.withdraw()  # 禁用tkinter主窗口
toast = ToastNotifier()
windows_ver = win32_ver()

# 如果正确导入了ico文件则设置tkinter对话框图标
if path.exists(path.join(basedir, 'wangluo.ico')):
    win.iconbitmap(path.join(basedir, 'wangluo.ico'))
    icon_path = path.join(basedir, 'wangluo.ico')
else:
    icon_path = 'wangluo.ico'


# 目前未联网，尝试联网
def not_connected(system_type):
    # 目前状态：未联网
    status = network_manager.connect_network()
    if status['result'] == 'success' and status['message'] == '':
        if system_type == 'Windows' and windows_ver[0] == '10':
            toast.show_toast(u'联网成功', u'网络已连接！', icon_path=icon_path, duration=5)
        else:
            messagebox.showinfo(title='网络已连接', message='联网成功！')
    elif status['result'] == 'success' and status['message'] != '':
        if system_type == 'Windows' and windows_ver[0] == '10':
            toast.show_toast(u'联网成功', status['message'], icon_path=icon_path, duration=10)  # 增加超时时长看消息内容
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
    f = rwjson.read_json()
    if f[0]['enable_disconnect']:
        # 询问是否需要断网
        yesno1 = messagebox.askyesno(title='网络已连接', message='设备目前已联网，是否需要断网？', icon='info')
        if yesno1:
            # 用户选择断网，尝试断网
            status = network_manager.disconnect_network()
            if status['result'] == 'success':
                if system_type == 'Windows' and windows_ver[0] == '10':
                    toast.show_toast(u'已断网', u'断网成功！', icon_path=icon_path, duration=5)
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
    else:
        # 配置文件未启用"enable_disconnect"，程序自动退出
        sys.exit(0)


def main(system_type):
    # 先判断网络通断再执行操作
    # noinspection PyBroadException
    try:
        if system_type == 'Windows':
            result = system(u'ping 119.29.29.29 -n 1 -w 1500')
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE  # default
            # CREATE_NO_WINDOW = 0x08000000
            DETACHED_PROCESS = 0x00000008
            subprocess.call('taskkill /F /IM exename.exe', startupinfo=si, creationflags=DETACHED_PROCESS, shell=False)
        else:
            result = system(u'ping 119.29.29.29 -c 1 -W 1500')
        if result == 0:
            connected(system_type)
        else:
            not_connected(system_type)
    except Exception as e:
        error_message = '出现未知错误，无法判断网络通断情况！\n是否要尝试联网？\n错误信息：' + str(e)
        yesno = messagebox.askyesno(title='未知错误', message=error_message, icon='error')
        if yesno:
            # 用户选择联网
            not_connected(system_type)
        else:
            # 用户选择不联网，程序自动退出
            sys.exit(1)


if __name__ == '__main__':
    # 判断系统类型
    system_type = os_type()
    if system_type == 'Windows':
        # 检测多开
        mutex_name = 'school_network'
        mutex = CreateMutex(None, False, mutex_name)
        if GetLastError() == ERROR_ALREADY_EXISTS:
            messagebox.showerror(title='警告', message='本程序不能同时运行多个实例，请不要多开。\n若右下角仍有本程序通知，请关掉通知后重试！')
            sys.exit(0)
        else:
            main(system_type)
    else:
        # 系统不是Windows，直接启动
        main(system_type)
