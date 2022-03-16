#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from os.path import dirname, join
from tkinter.messagebox import showerror, showwarning

import yaml

current_config_version = 3
config_path = join(dirname(sys.argv[0]), 'config.yml')


def str_value(target: dict):
    for k, v in target.items():
        if isinstance(v, dict):
            str_value(v)
        elif isinstance(v, int):  # True / False 也会被处理
            target[k] = str(v).lower()
        elif v is None:
            target[k] = ''
    return target


# 写入配置文件
def write_json():
    text = '''\
# 本配置文件内容需要根据学校服务器设置动态调整
main:
  version: 3 # 配置文件版本号，请勿更改

funtion:
  check_school_network: true # 是否检查校园网环境
  disconnect_network: true # 是否开启断网功能

url:
  server: http://127.0.0.1 # 校园网登录服务器的地址，用于判断当前网络环境是否为校园网环境
  login: /eportal/InterFace.do?method=login # 校园网登录地址，无需服务器地址
  logout: /eportal/InterFace.do?method=logout # 校园网断线地址，无需服务器地址

# 请根据抓包结果调整条目与内容
cookie: ''

# 请根据抓包结果调整条目与内容（?key1=value1&key2=value2）
# 请不要在密码栏填入明文密码
login_data:
  userId: '00000000000'
  password:
  service:
  queryString:
  operatorPwd:
  operatorUserId:
  validcode:
  passwordEncrypt: true

# 一般来说不填参数也能用，但请不要删除（?key1=value1&key2=value2）
logout_data:

headers:
  Referer:
'''

    try:
        with open(config_path, 'w', encoding='utf-8') as fp:
            fp.write(text)
    except Exception as e:
        error_message = f'尝试写入新配置文件时出错\n{e}'
        showerror(title='错误', message=error_message)
        exit(1)


def read_cfg() -> dict:
    """读取配置文件，没有做异常处理及日志记录，因此在配置文件出错时可能比较难查找原因，建议重新生成"""
    try:
        with open(config_path, 'r', encoding='utf-8') as fp:
            cfg = yaml.safe_load(fp)
    except IOError:
        write_json()
        showwarning(title='警告', message='配置文件不存在，已生成新配置文件，请填写配置文件后重试!')
        sys.exit(1)
    except Exception as e:
        error_message = f'尝试读取配置文件时出错\n{e}'
        showerror(title='错误', message=error_message)
        sys.exit(1)

    config_version = cfg['main'].get('version', 0)
    if config_version < current_config_version:
        showwarning(title='警告', message='读取配置文件时出错：\n配置文件格式过期，请备份并删除原配置文件后运行本程序重新生成！')
        sys.exit(1)
    elif config_version > current_config_version:
        showwarning(title='警告', message='读取配置文件时出错：\n配置文件版本过高，请更新本程序。\n' '如您使用的程序已是最新版本，请勿更改配置文件中"config_version"的值！')
        sys.exit(1)

    for key in cfg:
        if key in ['url', 'login_data', 'logout_data'] and cfg[key] is not None:
            cfg[key] = str_value(cfg[key])

    if cfg['login_data']['userId'] == '00000000000':
        showwarning(title='警告', message='配置文件未正确填写，请填写配置文件后重试!')
        sys.exit(1)

    if cfg['url']['server'][-1] == '/':
        cfg['url']['server'] = cfg['url']['server'][:-1]

    if cfg['logout_data'] is None:
        cfg['logout_data'] = {}

    return cfg
