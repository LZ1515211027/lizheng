# -*- coding: utf-8 -*-
import openpyxl
import SADP
from public_function import getColValues
import threading
import sys
reload(sys)
sys.setdefaultencoding('utf8')


# 读取Excel信息
class Excel:

    # 初始化
    def __init__(self):
        self.filename   = 'devices/devices.xlsx'  # 读取的文件名
        self.serialno   = []              # 设备序列号
        self.ip         = []              # 设备ip
        self.gateway    = []              # 设备网关
        self.subnetmask = []              # 设备子网掩码
        self.password   = []              # 设备密码

    def read(self):
        # 读取Excel
        try:
            data = openpyxl.load_workbook(self.filename)

            # 读取Sheet1表
            read = data[u'SADP激活']

            # 获取设备IP与格式化次数
            self.serialno   =   list(filter(None, getColValues(read, 1)))[1:]
            self.ip         =   list(filter(None, getColValues(read, 2)))[1:]
            self.gateway    =   list(filter(None, getColValues(read, 3)))[1:]
            self.subnetmask =   list(filter(None, getColValues(read, 4)))[1:]
            self.password   =   list(filter(None, getColValues(read, 5)))[1:]
            return True
        except Exception as e:
            print(e)
            return False

# 多线程执行
class MyThread(threading.Thread):

    def __init__(self, sadp, serialno, ip, gateway, subnetwask, password):
        threading.Thread.__init__(self)
        self.sadp = sadp
        self.serialno = serialno
        self.ip = ip
        self.gateway = gateway
        self.subnetmask = subnetwask
        self.password = password
        self.result = ''
        self.activate_status = -1

    def run(self):
        # 检查设备激活状态
        if self.check_activated_status():
            # 未激活，则激活
            if self.activate_status == 1:
                if self.activate_device():
                    if self.set_parameters():
                        print(u'序列号{0}:激活并配置网络参数成功'.format(self.serialno))
            # 已激活，则跳过激活步骤
            else:
                if self.set_parameters():
                    print(u'序列号{0}:激活并配置网络参数成功'.format(self.serialno))

    def check_activated_status(self):
        device_info = self.sadp.sadp_get_online_devices_info('SerialNO', self.serialno)
        if device_info != []:
            if device_info[0]['Activated'] == 1:
                self.activate_status = 1
                return True
            else:
                self.activate_status = 0
                return True
        else:
            print(u'序列号{0}：获取激活状态失败，不执行激活配置操作'.format(self.serialno))
            self.result = u'序列号{0}：获取激活状态失败，不执行激活配置操作'.format(self.serialno)
            return False

    def activate_device(self):
        n = 0
        while True:
            try:
                n += 1
                ret,status = self.sadp.sadp_activate_device_by_serial_no(serial_no=self.serialno, password=self.password)
                if n == 4 and status is False:
                    self.result = ret
                    return False
                if status is False:
                    continue
                else:
                    return True
            except Exception as e:
                if n == 3:
                    self.result = u'序列号{0}:激活失败，报错信息：{1}'.format(self.serialno,e)
                    return False

    def set_parameters(self):
        n = 0
        while True:
            try:
                n += 1
                self.sadp.sadp_modify_device_net_parameters(condition='serialno', condition_value=self.serialno,
                                                            Password=self.password, IP=self.ip, GateWay=self.gateway,
                                                            SubNetMask=self.subnetmask)
                return True
            except Exception as e:
                if n == 3:
                    self.result = u'序列号{0}:激活成功但配置网络参数失败，报错信息：{1}'.format(self.serialno,e)
                    return False

def sadp_activate():
    print(u'开始执行')
    result_r = []
    excel = Excel()
    if excel.read():
        # 初始化SADP模块
        sadp = SADP.Sadp()
        sadp.sadp_start()
        serialno_list = sadp.sadp_get_online_devices_serialno()
        nums = len(excel.serialno)
        for i in serialno_list:
            for j in range(nums):
                if excel.serialno[j] in i:
                    excel.serialno[j] = i
        # 遍历设备序列号执行
        li = []
        for i in range(nums):
            t = MyThread(sadp, excel.serialno[i], excel.ip[i], excel.gateway[i],excel.subnetmask[i],excel.password[i])
            li.append(t)
            t.start()
        for t in li:
            t.join()
        print(u'执行完毕')
        for i in li:
            result_r.append(i.result)
    return result_r

if __name__ == '__main__':
    A = sadp_activate()
    print(A)

