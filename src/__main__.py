#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from json import loads as json_loads
from os import path
from platform import system as os_type
from platform import win32_ver
from tkinter import messagebox, Tk
from urllib.request import urlopen

from requests import post
from win10toast import ToastNotifier
from win32api import GetLastError
from win32event import CreateMutex
from winerror import ERROR_ALREADY_EXISTS

import config

# 使 pyinstaller 能正确导入ico文件
if getattr(sys, 'frozen', None):
    basedir = sys._MEIPASS  # noqa
else:
    basedir = path.dirname(__file__)

win = Tk()
win.withdraw()  # 禁用tkinter主窗口
# 设置tkinter对话框与win10 toast的图标
if path.exists(path.join(basedir, 'wangluo.ico')):
    win.iconbitmap(path.join(basedir, 'wangluo.ico'))
    icon_path = path.join(basedir, 'wangluo.ico')

os_type = os_type()
if os_type == 'Windows':
    toast = ToastNotifier()
    windows_ver = win32_ver()
    is_win = True
    is_win10 = True if windows_ver[0] == '10' else False  # 如果windows版本等于10则is_win10为True，否则为False
else:
    is_win = False
    is_win10 = False

cfg = config.read_cfg()  # 读取配置文件


def showinfo(title='Ruijie ePorta Tool', msg='test', wait_time=5):
    """
    发送tkinter通知框或win10的toast

    :param title: 通知标题
    :param msg: 通知内容
    :param wait_time: toast的展示时长
    """

    if is_win and is_win10:
        toast.show_toast(title=title, msg=msg, icon_path=icon_path, duration=wait_time, threaded=True)
    else:
        messagebox.showinfo(title=title, message=msg)


def is_connected(host='https://www.baidu.com', timeout=0.5) -> bool:
    """
    测试网络通断状态

    :param host: 用于测试连接状态的地址（带 `http://` 或 `https://` 前缀）
    :param timeout: 超时时间（单位：秒）
    :return: 布尔值，True 为通，False 为不通
    """

    try:
        urlopen(host, timeout=timeout)  # Python 3.x
        return True
    except:  # noqa
        return False


def connected():
    """
    当目前已联网时要执行的操作

    获取配置文件中填写好的header、data、cookie并发送至登录服务器，然后从服务器返回的json文本中判断结果
    """

    # 询问用户是否需要断网
    if messagebox.askyesno(title='网络已连接', message='设备目前已联网，是否需要断网？', icon='info'):
        # 用户选择断网，尝试断网
        url = cfg['server']['logout_url']
        data = cfg['logout_data']
        header = cfg['logout_header']
        cookie = cfg['cookie']

        try:
            res = post(url=url, data=data, headers=header, cookies=cookie)
        except Exception as e:
            error_message = f'出现错误！\n\n错误信息：{str(e)}'
            messagebox.showerror(title='未知错误', message=error_message)
            sys.exit(1)
        else:
            res.encoding = 'utf-8'
            status = json_loads(res.text)
            if status['result'] == 'success':
                showinfo(title='已断网', msg='断网成功！', wait_time=5)
            elif status['result'] == 'fail':
                error_message = f'断网失败！\n失败原因：{status["message"]}'
                messagebox.showerror(title='断网失败', message=error_message)
            else:
                error_message = f'未知错误：{str(status)}'
                messagebox.showerror(title='错误', message=error_message)
            print('服务器返回内容：', status)
    sys.exit(0)


def disconnected():
    """
    当目前没有联网时要执行的操作

    获取配置文件中填写好的header、data、cookie并发送至登录服务器，然后从服务器返回的json文本中判断结果
    """

    url = cfg['server']['login_url']
    data = cfg['login_data']
    header = cfg['login_header']

    try:
        res = post(url=url, data=data, headers=header)
    except Exception as e:
        error_message = f'出现错误！\n\n错误信息：{str(e)}'
        messagebox.showerror(title='未知错误', message=error_message)
        sys.exit(1)
    else:
        res.encoding = 'utf-8'
        status = json_loads(res.text)
        if status['result'] == 'success' and status['message'] == '':
            showinfo(title='联网成功', msg='网络已连接！', wait_time=6)
        elif status['result'] == 'success' and status['message'] != '':
            showinfo(title='联网成功', msg=status['message'], wait_time=6)
        elif status['result'] == 'fail':
            error_message = '联网失败！\n失败原因：' + status['message']
            messagebox.showerror(title='联网失败', message=error_message)
        elif status['result'] != 'success' and status['result'] != 'fail':
            error_message = '未知错误：' + str(status)
            messagebox.showerror(title='错误', message=error_message)
        print('服务器返回内容：', status)
    sys.exit(0)


def main():
    """
    主函数，判断网络通断情况并执行相应操作
    """

    # 先判断网络通断再执行操作
    if cfg['config']['enable_network_status_check']:  # 读配置文件，是否需要判断网络通断
        if is_connected():  # 判断网络通断
            connected()
        else:
            if cfg['config']['enable_school_network_check']:
                if not is_connected(host=cfg["config"]["server_url"], timeout=0.3):  # 判断是否能连接到登录服务器
                    # 如果无法连接到登录服务器则发送通知并退出
                    showinfo(title='网络环境错误', msg='当前不在校园网环境，不自动尝试连接校园网')
                    sys.exit(0)
                else:
                    disconnected()
            else:
                disconnected()  # 如果不判断是否能连接到登录服务器，则
    else:
        disconnected()  # 配置文件未启用"enable_network_status_check"，程序将始终当作设备未联网


if __name__ == '__main__':
    # 判断系统类型
    try:
        if is_win:
            # 检测多开
            mutex_name = 'ruijie_eporta_tool'  # noqa
            mutex = CreateMutex(None, False, mutex_name)
            if GetLastError() == ERROR_ALREADY_EXISTS:
                messagebox.showerror(title='警告', message='本程序不能同时运行多个实例，请不要多开。\n若右下角仍有本程序通知，请关掉通知后重试！')
                sys.exit(0)
            else:
                main()
        else:
            # 系统不是Windows，直接启动（没有Linux环境也懒得搞）
            main()
    except KeyboardInterrupt:
        sys.exit()
