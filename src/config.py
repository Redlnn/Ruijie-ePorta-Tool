#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from json import dump as json_dump
from json import load as json_load
from os import path
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

current_config_version = 2


# 写入配置文件
def write_json():
    tips = {
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
        '重要提醒': '请不要随意修改config_version的值！',
        'config_version': current_config_version,
        '选项解释-enable_school_network_check': '指是否需要判断当前网络环境是否为校园网环境，若设置为false则不检测',
        'enable_school_network_check': True,
        '选项解释-server_url': '校园网登录服务器的地址用于判断当前网络环境是否为校园网环境',
        'server_url': 'http://127.0.0.1',
        '选项解释-enable_network_status_check': '是否判断网络通断，开启后在网络已连接时运行本程序将弹出是否需要断网的对话框',
        'enable_network_status_check': True
    }
    # 上下线时所连接的服务器的地址
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
                      'Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.62 Edge/18.19041',
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
                      'Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.62 Edge/18.19041',
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
        'tips': tips,
        'config': config,
        'server': server,
        'cookie': cookie,
        'login_data': login_data,
        'login_header': login_header,
        'logout_data': logout_data,
        'logout_header': logout_header,
    }

    try:
        with open('config.json', 'w', encoding='utf-8') as f:
            json_dump(all_json, f, ensure_ascii=False, indent=4)
    except Exception as e:
        error_message = f'尝试写入新配置文件时出错\n{str(e)}'
        messagebox.showerror(title='错误', message=error_message)
        sys.exit(1)


def read_cfg():
    try:
        f = open('config.json', mode='r', encoding='utf-8')
    except IOError:
        write_json()
        messagebox.showwarning(title='警告', message='配置文件不存在，已生成新配置文件，请填写配置文件后重试!')
        sys.exit(1)
    else:
        config = json_load(f)  # 读取配置文件
        f.close()
        # 检测配置文件版本
        if not config['config']['config_version']:
            messagebox.showerror(title='警告', message='读取配置文件时出错，原因：\n\n    配置文件格式过期，请备份并删除原配置文件后运行本程序重新生成！')
            sys.exit(1)
        else:
            if config['config']['config_version'] < current_config_version:
                messagebox.showerror(title='警告', message='读取配置文件时出错，原因：\n\n    配置文件格式过期，请备份并删除原配置文件后运行本程序重新生成！')
                sys.exit(1)
            elif config['config']['config_version'] > current_config_version:
                messagebox.showerror(title='警告', message='读取配置文件时出错，原因：\n\n    配置文件版本过高，请更新本程序。\n'
                                                         '    如您使用的程序已是最新，请勿更改配置文件中"config_version"的值')
                sys.exit(1)

        if config['login_data']['userId'] == '00000000000':
            messagebox.showwarning(title='警告', message='配置文件未正确填写，请填写配置文件后重试!')
            sys.exit(1)
        return config
