# -*- coding: utf-8 -*-
import requests
from requests.auth import HTTPDigestAuth
import xmltodict
from variable import *
import openpyxl
from public_function import getColValues
from lxml import etree
from public_function import sort_file_by_time
import os
import time
import threading
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class Device:
    """
    ip:设备ip
    username：设备登录账号
    password:设备密码
    nas_address:nas盘地址，选填
    nas_file_path:nas盘文件路径，选填
    restore_choose:是否简单恢复，选填
    record_channel:录像通道
    """

    # 初始化用户输入的ip、HTTP端口号、用户名、密码等
    def __init__(self, nvr_ip, username, password, path):
        self.port = '80'  # 设备HTTP端口号
        self.username = username  # 帐户名
        self.password = password  # 密码
        self.nvr_ip = nvr_ip  # nvr地址
        self.path = path
        self.version = 0

    # SD卡兼容性：检查设备是否上线
    def check_status(self):
        n = 0
        while True:
            try:
                n += 1
                put = requests.get('http://{0}:{1}{2}'.format(self.nvr_ip, self.port, check_status_url),
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=10)
                put.raise_for_status()
                print(u"设备上线成功！！")
                return True
            except Exception as e:
                # 若超过2分钟未检测到设备在线，报错
                if n >= 48:
                    return False


    # SD卡兼容性：重启
    def reboot(self):
        # 重启执行
        try:
            print(u"设备开始重启")
            put = requests.put('http://{0}:{1}{2}'.format(self.nvr_ip, self.port, reboot_url),
                               auth=HTTPDigestAuth(self.username, self.password), timeout=10)
            put.raise_for_status()
            st = time.time()
            time.sleep(30)
            if self.check_status():
                et = time.time()
                return True
            else:
                print(u"设备长达8分钟未起来，请检查！！")
                return False
        except Exception as e:
            print(u"执行重启操作失败！")
            return False


    def test(self):
        try:
            self.update()

        except Exception as e:
                    print(u"设备{0}:导入NVR失败")

    # 检查设备版本号
    def check_nvr_version(self):
        n = 0
        while True:
            try:
                n += 1
                get = requests.get('http://{0}:{1}{2}'.format(self.nvr_ip, self.port, check_status_url),
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                get.raise_for_status()
                get_text = xmltodict.parse(get.text)
                self.version = int(get_text['DeviceInfo']['firmwareReleasedDate'][-6:])
                # print(self.version)
                return True
            except Exception as e:
                if n >= 2:
                    print(e)
                    return False

   # 升级
    def update(self):
        with open(self.path, 'rb') as f:
            self.session = requests.Session()
            self.session.auth = HTTPDigestAuth(self.username, self.password)
            page = self.session.get('http://{0}:{1}{2}'.format(self.nvr_ip, self.port, check_status_url), timeout=10, verify=False)
            print(page.status_code)
            # url = 'http://{0}:{1}{2}'.format(self.nvr_ip, self.port, update_url)
            # print(url)
            # ontent = self.session.put(url, data=f, timeout=10000, verify=False)
            # print(ontent.text)
            # url2 = 'http://{0}:{1}{2}'.format(self.nvr_ip, self.port, '/ISAPI/System/reboot')
            # ontent2 = self.session.put(url2, timeout=1000, verify=False)
            # print(ontent2.text)
        return True


# 读取Excel信息
class Excel:

    # 初始化
    def __init__(self):
        self.filename = 'devices.xlsx'  # 读取的文件名
        self.nvr_ip = []                        # nvr地址
        self.path = []                      # 协议

    def read(self):
        # 读取Excel
            data = openpyxl.load_workbook(self.filename)

            # 读取Sheet1表
            read = data[u'NVR信息']
            # 获取设备IP与格式化次数
            self.nvr_ip = list(filter(None, getColValues(read, 1)))[1:]  # nvr地址
            self.username = list(filter(None, getColValues(read, 2)))[1:]  # nvr地址
            self.password =  list(filter(None, getColValues(read, 3)))[1:]  # nvr地址
            self.path = list(filter(None, getColValues(read, 4)))[1:]  # SVN路径
            print(1)
            return True



# 多线程执行
class MyThread(threading.Thread, Device):

    def __init__(self, nvr_ip, username, password, path):
        threading.Thread.__init__(self)
        Device.__init__(self, nvr_ip, username, password, path)

    def run(self):
        self.test()


# 从读取到生成报告总流程
def NVR_UPDATE():
        print(u'开始执行')
        excel = Excel()
        if excel.read():
            nums = len(excel.nvr_ip)
            li = []
            for i in range(nums):
                t = MyThread(excel.nvr_ip[i], excel.username[i], excel.password[i], excel.path[i])
                li.append(t)
                t.start()
            for t in li:
                t.join()
        print(u'执行结束')

if __name__ == '__main__':
    NVR_UPDATE()
