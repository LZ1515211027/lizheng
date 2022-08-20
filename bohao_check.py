# -*- coding:utf-8 -*-
import requests                           # 请求相关的库
import sys
from requests.auth import HTTPDigestAuth  # 摘要认证
import threading
import openpyxl
import xmltodict
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
    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.result = u'拨号正常'

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

    # 拨号检查
    def bohao_check(self):
        try:
            get = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, bohao_url),
                               auth=HTTPDigestAuth(self.username, self.password), timeout=10)
            get.raise_for_status()
            get_text = xmltodict.parse(get.text)
            check = get_text['Dialstatus']['Dialstat']
            if check == 'connected':
                self.result = u'{0}：连接正常'.format(self.ip)
                print(u"{0}：连接正常".format(self.ip))
                return True
            else:
                self.result = u"{0}：连接异常，{1}".format(self.ip, check)
                print(u"{0}：连接异常，{1}".format(self.ip, check))
                return False
        except Exception as e:
            print(u"{0}：获取拨号状态失败".format(self.ip))
            self.result = u'{0}：获取拨号状态失败'.format(self.ip)
            return False

    # 业务流程
    def test(self):
        if not self.check():
            print(u"{0}：不在线，请检查".format(self.ip))
            self.result = u'{0}：不在线，请检查'.format(self.ip)
            return
        self.bohao_check()

# 多线程运行
class MyThread(threading.Thread, Device):

    def __init__(self, ip, port, username, password):
        threading.Thread.__init__(self)
        Device.__init__(self, ip, port, username, password)

    def run(self):
        self.test()


# 从读取参数到执行逻辑
def bohao_check():
    try:
        # 读取参数信息
        data = openpyxl.load_workbook('devices/devices.xlsx')
        table = data[u'拨号状态检查']
        devices  = list(filter(None, getColValues(table, 1)))[1:]
        username = list(filter(None, getColValues(table, 2)))[1:]
        password = list(filter(None, getColValues(table, 3)))[1:]
        length = len(devices)

        # 执行逻辑
        li = []
        print(u"开始执行!!")
        for i in range(length):
            t = MyThread(devices[i], '80', username[i], password[i])
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