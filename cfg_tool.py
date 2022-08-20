# -*- coding:utf-8 -*-
import requests                           # 请求相关的库
import os
import sys
from requests.auth import HTTPDigestAuth  # 摘要认证
import threading
import openpyxl
from variable import *
from public_function import getColValues
reload(sys)
sys.setdefaultencoding('utf8')


class Device:
    """
    ip:设备ip
    port:设备HTTP端口号
    username：设备登录账号
    password:设备密码
    mode:导出Or导入
    cfg_password:参数密码
    """

    # 初始化
    def __init__(self, ip, port, username, password, mode, cfg_password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.result = u'执行通过'
        self.mode = mode

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        # 参数文件保存路径
        self.file_path = os.path.join(application_path + '/Config_file/' + self.ip).replace('\\','/')
        self.parm = {"secretkey": cfg_password}

    # 登录设备
    def check(self):
        n = 0
        while True:
            try:
                n += 1
                put = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, check_status_url),
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                put.raise_for_status()
                return True
            except Exception as e:
                if n >= 2:
                    return False

    # 参数导出
    def parm_output(self):
        try:
            get = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, parm_url), params=self.parm,
                               auth=HTTPDigestAuth(self.username, self.password))
            get.raise_for_status()
            with open(self.file_path, "wb") as file:
                file.write(get.content)
            print(u"IP:{0} 参数导出成功".format(self.ip))
            return True
        except Exception as e:
            print(u"IP:{0} 参数导出失败".format(self.ip))
            self.result = u'{0}：参数导出失败'.format(self.ip)
            return False

    # 参数导入
    def parm_input(self):
        try:
            with open(self.file_path, 'rb') as file:
                put = requests.put('http://{0}:{1}{2}'.format(self.ip, self.port, parm_url), params=self.parm,data=file.read(),
                                    auth=HTTPDigestAuth(self.username, self.password),timeout=120)
            put.raise_for_status()
            reboot = requests.put('http://{0}:{1}{2}'.format(self.ip, self.port, reboot_url),
                               auth=HTTPDigestAuth(self.username, self.password), timeout=120)
            reboot.raise_for_status()
            print(u"IP:{0} 参数导入成功".format(self.ip))
            return True
        except Exception as e:
            print(e)
            print(u"IP:{0} 参数导入失败".format(self.ip))
            self.result = u'{0}：参数导入失败'.format(self.ip)
            return False

    # 业务流程
    def test(self):
        if self.mode == u'导出':
            if not self.check():
                print(u"IP:{0} 不在线，请检查".format(self.ip))
                self.result = u'{0}：不在线，请检查'.format(self.ip)
                return
            self.parm_output()
        elif self.mode == u'导入':
            if not self.check():
                print(u"IP:{0} 不在线，请检查".format(self.ip))
                self.result = u'{0}：不在线，请检查'.format(self.ip)
                return
            self.parm_input()
        else:
            print(u"Excel数据有误，请检查")
            self.result = u'Excel数据有误，请检查'


# 多线程运行
class MyThread(threading.Thread, Device):

    def __init__(self, ip, port, username, password, mode, cfg_password):
        threading.Thread.__init__(self)
        Device.__init__(self, ip, port, username, password, mode, cfg_password)

    def run(self):
        self.test()


# 从读取参数到执行逻辑
def cfg(mode):
    try:
        # 读取参数信息
        data = openpyxl.load_workbook('devices/devices.xlsx')
        if mode == u'导出':
            table = data[u'批量参数导出']
        elif mode ==u'导入':
            table = data[u'批量参数导入']
        devices  = list(filter(None, getColValues(table, 1)))[1:]
        parm_pwd    = list(filter(None, getColValues(table, 2)))[1:]
        username = list(filter(None, getColValues(table, 3)))[1:]
        password = list(filter(None, getColValues(table, 4)))[1:]
        length = len(devices)

        # 执行逻辑
        li = []
        print(u"开始执行!!")
        for i in range(length):
            t = MyThread(devices[i], '80', username[i], password[i],
                         mode, parm_pwd[i])
            li.append(t)
            t.start()
        for t in li:
            t.join()
        result = []
        for i in li:
            result.append(i.result)
        print(u"执行完毕!!")
        return result
    except Exception as e:
        print(e)
        return e