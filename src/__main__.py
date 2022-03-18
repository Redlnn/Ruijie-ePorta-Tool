#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
from datetime import datetime
from json import loads as json_loads
from os.path import dirname, join
from platform import system as os_type
from platform import win32_ver
from time import sleep
from tkinter import Tk
from tkinter.messagebox import askyesno, showerror, showinfo
from urllib import parse, request
from urllib.request import urlopen

from tinyWinToast.tinyWinToast import Toast

from config import read_cfg

# 使 pyinstaller 能正确导入ico文件
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']  # type: ignore # noqa
    basedir = sys._MEIPASS  # type: ignore # noqa
else:
    basedir = dirname(__file__)

icon_path = join(basedir, 'wangluo.ico')


class MyToast(Toast):
    def show(self):
        toaststr = self.__genXML()
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(["PowerShell", "-Command", toaststr], startupinfo=si)


win = Tk()
win.withdraw()  # 禁用tkinter主窗口
win.iconbitmap(icon_path)  # 设置tkinter对话框与win10 toast的图标

is_win = False
is_win10 = False

if os_type() == 'Windows':
    is_win = True
    if win32_ver()[0] in ('10', '11'):
        is_win10 = True

cfg = read_cfg()

headers = {
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.39',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cookie': parse.quote(cfg['cookie']),
    'Host': cfg['url']['server'].replace('http://', '').replace('https://', ''),
    'Origin': cfg['url']['server'],
}

headers.update(cfg['headers'])

login_data = cfg['login_data']
logout_data = cfg['logout_data']


def notify(title: str = '锐捷 ePorta 连接工具', msg: str = ''):
    """发送 tkinter 对话框或 win10+ 的 toast 通知

    :param title: 通知标题
    :param msg: 通知内容
    :param duration: toast的展示时长
    """

    if is_win and is_win10:
        toast = Toast()
        toast.setAppID('锐捷 ePorta 连接工具')
        toast.setTime(datetime.now().replace(microsecond=0).isoformat() + 'Z')
        toast.setTitle(title)
        toast.setMessage(msg, maxLines=5)
        toast.setIcon(src=icon_path)
        toast.addText(msg='锐捷 ePorta 连接工具', placement='attribution')
        toast.show()
    else:
        showinfo(title=title, message=msg)


def test_internet(host: str = 'http://connect.rom.miui.com/generate_204', timeout: int = 1) -> bool:
    """测试网络通断状态

    Args:
        host(str): 用于测试连接状态的generate_204服务器地址
        timeout(int): 超时时间（单位：秒）

    Returns:
        bool: True表示连接正常，False表示连接异常
    """

    try:
        resp = urlopen(host, timeout=timeout)
        if host.endswith('generate_204'):
            return True if resp.status == 204 else False
        elif 200 <= resp.status <= 208 or resp.status == 226:
            return True
        return False
    except:  # noqa
        return False


def disconnect():
    """当目前已联网时要执行的操作"""

    resp = request.Request(
        cfg['url']['server'] + cfg['url']['logout'],
        data=bytes(parse.urlencode(login_data).encode('utf-8')),
        headers=headers,
        origin_req_host=None,
        unverifiable=False,
        method='POST',
    )

    try:
        res = request.urlopen(resp, timeout=10)
    except Exception as e:
        error_message = f'出现错误:\n{str(e)}'
        showerror(title='未知错误', message=error_message)
        sys.exit(1)
    else:
        status = json_loads(res.read().decode())
        if status['result'] == 'success':
            notify(title='已断网', msg='断网成功！')
        elif status['result'] == 'fail':
            showerror(title='断网失败', message=f'断网失败:\n{status["message"]}')
        else:
            showerror(title='错误', message=f'未知错误：{status}')


def connect():
    """当目前没有联网时要执行的操作"""

    resp = request.Request(
        cfg['url']['server'] + cfg['url']['login'],
        data=bytes(parse.urlencode(login_data).encode('utf-8')) if login_data else None,
        headers=headers,
        origin_req_host=None,
        unverifiable=False,
        method='POST',
    )

    try:
        res = request.urlopen(resp, timeout=10)
    except Exception as e:
        showerror(title='未知错误', message=f'出现错误:\n{str(e)}')
        sys.exit(1)
    else:
        status = json_loads(res.read().decode())
        if status['result'] == 'success' and status['message'] == '':
            notify(title='联网成功', msg='网络已连接！')
        elif status['result'] == 'success' and status['message'] != '':
            notify(title='联网成功', msg=status['message'])
        elif status['result'] == 'fail':
            showerror(title='联网失败', message=f'未知错误:\n{status["message"]}')
        elif status['result'] != 'success' and status['result'] != 'fail':
            showerror(title='错误', message=f'未知错误:\n{status}')


def main():
    if cfg['funtion']['check_school_network']:  # 通过是否能连接到校园网登录服务器判断当前网络环境是否在校园网内
        if not test_internet(host=cfg['url']['server'], timeout=3):
            notify(title='非校园网环境', msg='当前不在校园网环境，10s后重新检测\n若您的系统刚启动，可能还没反应过来，没有连上任何网络，为正常现象')
            sleep(10)
            if not test_internet(host=cfg['url']['server'], timeout=2):
                notify(title='非校园网环境', msg='当前不在校园网环境，不自动尝试联网，程序自动退出')
                sys.exit(0)
    if test_internet():
        if cfg['funtion']['disconnect_network']:
            if askyesno(title='网络已连接', message='设备目前已联网，是否需要断网？', icon='info'):
                disconnect()
            sys.exit(0)
        else:
            notify(title='设备已联网', msg='网络本来就是通的噢~')
    connect()


if __name__ == '__main__':
    if is_win:
        from win32api import GetLastError
        from win32event import CreateMutex
        from winerror import ERROR_ALREADY_EXISTS

        # 检测多开
        mutex_name = 'ruijie_eporta_tool'
        mutex = CreateMutex(None, False, mutex_name)  # type: ignore # noqa
        if GetLastError() == ERROR_ALREADY_EXISTS:
            showerror(title='警告', message='本程序不可多开。\n若右下角仍有本程序通知，请关掉通知后重试！')
            sys.exit(0)
    main()
