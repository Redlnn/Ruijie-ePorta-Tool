#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys
from json import dump as json_dump
from json import load as json_load
from os import path, system
from tkinter import messagebox, Tk

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


# 写入配置文件
def write_json():
    warn = {
        '警告1': '除非抓到的包中有更多的参数，否则请不要增删本配置文件中的任何条目或改动顺序',
        '提示1': '本配置文件内容可能需要根据学校服务器设置及时更新',
        '提示2': '以下为各大项配置的用途解释',
        'config': '本程序配置',
        'server': '上下线时所连接的服务器的地址，请按格式填写',
        'login_data': '上线联网时发送的参数，请按需增删',
        'logout_data': '下线断网时发送的参数，请按需增删',
        'login_header': '上线联网时使用的 HTML Header，Referer 项必填，Origin 项不改的话就删掉，其他项请按需增删',
        'logout_header': '下线断网时使用的 HTML Header，Referer 项必填，Origin 项不改的话就删掉，其他项请按需增删',
        'cookie': '连接登录服务器所使用的cookie，请在抓包时选择好运营商以及保存密码'
    }
    # 程序设置
    config = {
        '请不要随意修改config_version的值': '',
        'config_version': 1,
        'allow_ping 指校园网登录服务器是否允许ping': '根据下面server项的值ping，若关闭则不检测是否为校园网环境',
        '请填写校园网登录页的地址，不带http://或https://，结尾也不要有斜杠': '只填写ip或xx.xxx.com格式即可',
        'allow_ping': True,
        'server': '127.0.0.1',
        'enable_disconnect 用于控制本程序是否判断网络通断以及在网络已连接时运行本程序是否弹出断网对话框': '',
        '关闭后本程序将不再判断网络状况，始终当作设备未联网': '关闭本选项以及上方的 allow_ping 后将不会弹出 ping 命令的 CMD 窗口',
        'enable_disconnect': True
    }
    # 登录与登出所使用目标服务器地址
    server = {
        'login_url': 'http://127.0.0.1/eportal/InterFace.do?method=login',
        'logout_url': 'http://127.0.0.1/eportal/InterFace.do?method=logout',
    }
    # 登录时传入参数
    login_data = {
        'userId': '00000000000',
        'password': '',
        'service': '',
        'queryString': '',
        'operatorPwd': '',
        'operatorUserId': '',
        'validcode': '',  # 图片验证码，若抓包中该项不为空，则不可以使用本程序
        'passwordEncrypt': ''
    }
    # 断线时传入参数
    logout_data = {
        'userIndex': '',
    }
    # 登录时的HTML Header
    login_header = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'Origin': 'http://127.0.0.1',
        'Referer': '',
    }
    # 断线时的HTML Header
    logout_header = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'Origin': 'http://127.0.0.1',
        'Referer': '',
    }

    cookie = {
        'EPORTAL_COOKIE_SAVEPASSWORD': 'tre',
        'EPORTAL_AUTO_LAND': '',
        'EPORTAL_COOKIE_USERNAME': '',
        'EPORTAL_COOKIE_OPERATORPWD': '',
        'EPORTAL_COOKIE_DOMAIN': '',
        'EPORTAL_COOKIE_PASSWORD': '',
        'EPORTAL_COOKIE_SERVER': '',
        'EPORTAL_COOKIE_SERVER_NAME': '',
        'EPORTAL_COOKIE_USER_GROUP_NAME': '',
        'JSESSIONID': ''
    }

    # 构造json文本
    all_json = {
        'warn': warn,
        'config': config,
        'server': server,
        'login_data': login_data,
        'logout_data': logout_data,
        'login_header': login_header,
        'logout_header': logout_header,
        'cookie': cookie,
    }

    # noinspection PyBroadException
    try:
        with open('./config.json', 'w', encoding='utf-8') as f:
            json_dump(all_json, f, ensure_ascii=False, indent=4)
        f.close()
    except Exception as e:
        error_message = '尝试写入新配置文件时出错\n' + str(e)
        messagebox.showerror(title='错误', message=error_message)
        sys.exit(1)


def read_json():
    try:
        f = open('./config.json', mode='r', encoding='utf-8')
    except IOError:
        write_json()
        messagebox.showwarning(title='警告', message='配置文件不存在，已生成新配置文件，请填写配置文件后重试!')
        sys.exit(1)
    else:
        config = json_load(f)  # 读取配置文件
        f.close()
        # 如果配置文件版本不存在或版本低于1
        if not config['config']['config_version'] or config['config']['config_version'] < 1:
            messagebox.showerror(title='警告', message='读取配置文件时出错，原因：\n\n    配置文件格式过期，请备份并删除原配置文件后运行本程序重新生成！')
            sys.exit(1)
        # 如果配置文件版本存在且版本大于1
        elif config['config']['config_version'] and config['config']['config_version'] > 1:
            messagebox.showerror(title='警告', message='读取配置文件时出错，原因：\n\n    配置文件版本过高，请更新本程序。\n'
                                                     '    如您使用的程序已是最新，请勿更改配置文件中"config_version"的值')
            sys.exit(1)

        if config['server']['login_url'] == 'http://127.0.0.1/eportal/InterFace.do?method=login' \
                or config['server']['logout_url'] == 'http://127.0.0.1/eportal/InterFace.do?method=logout':
            messagebox.showwarning(title='警告', message='配置文件未正确填写，请填写配置文件后重试!')
            sys.exit(1)
        return config
