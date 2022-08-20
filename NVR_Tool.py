# -*- coding: utf-8 -*-
import requests
from requests.auth import HTTPDigestAuth
import xmltodict
from variable import *
import openpyxl
from public_function import getColValues
from lxml import etree


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
    def __init__(self, ip, device_username, device_password, nvr_ip, nvr_username, nvr_password, protocol):
        self.ip = ip  # 设备地址
        self.channel = 1 # 设备通道数
        self.port = '80'  # 设备HTTP端口号
        self.nvr_ip = nvr_ip  # nas地址
        self.protocol = protocol
        self.result = u""
        if self.protocol == u'HIKVISION':
            self.nvr_port = '8000'
        elif self.protocol == u'HIKVISION增强':
            self.nvr_port = '8443'
        elif self.protocol == u'ONVIF':
            self.nvr_port = '80'
        else:
            self.nvr_port = '5060'
        self.device_username = device_username  # 设备用户名
        self.device_password = device_password  # 设备密码
        self.nvr_username = nvr_username  # 设备用户名
        self.nvr_password = nvr_password  # 设备密码

    # 获取通道数
    def check_channels(self):
        n = 0
        channel = 0
        while True:
            try:
                n += 1
                get = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, channel_url),
                                   auth=HTTPDigestAuth(self.device_username, self.device_password), timeout=3)
                get.raise_for_status()

                # 报文中遍历指定节点，获取通道数
                root = etree.XML(get.text.encode('utf-8'))
                VideoInputChannel = root.xpath("//*[local-name()='VideoInputChannel']")
                for _ in VideoInputChannel:
                    channel += 1
                self.channel = channel
                return True
            except Exception as e:
                if n >= 2:
                    print(e)
                    print(u"设备{0}:获取通道数失败".format(self.ip))
                    self.result = u"设备{0}:获取通道数失败".format(self.ip)
                    return False

    # 修改通道名
    def modify_channelName(self):
        try:
            for i in range(1,self.channel+1):
                get = requests.get(u'http://{0}:{1}{2}'.format(self.ip, self.port, channel_name_url) + str(i),
                                   auth=HTTPDigestAuth(self.device_username, self.device_password), timeout=6)
                get.raise_for_status()
                get_text = xmltodict.parse(get.text)
                get_text['VideoInputChannel']['name'] = self.ip + '-' + str(i)
                get_text['VideoInputChannel']['channelDescription'] = ''
                put_text = xmltodict.unparse(get_text)
                put = requests.put(u'http://{0}:{1}{2}'.format(self.ip, self.port, channel_name_url) + str(i),data=put_text,
                                   auth=HTTPDigestAuth(self.device_username, self.device_password))
                put.raise_for_status()
            return True
        except Exception as e:
            print(e)
            print(u"设备{0}:通道{1}获取通道数失败".format(self.ip,str(i)))
            self.result = u"设备{0}:通道{1}获取通道数失败".format(self.ip,str(i))
            return False

    # 获取通道数
    def check_nvr(self):
        try:
            get = requests.get('http://{0}:{1}{2}'.format(self.nvr_ip, self.port, nvr_channels_url),
                               auth=HTTPDigestAuth(self.nvr_username, self.nvr_password), timeout=15)
            get.raise_for_status()
            # 报文中遍历指定节点，获取通道数
            get_text = xmltodict.parse(get.text)
            put_text = xmltodict.unparse(get_text)
            position = '<ipAddress>{0}</ipAddress><managePortNo>{1}</managePortNo>'.format(self.ip,self.nvr_port)
            if position in put_text:
                print(u"设备{0}:NVR通道中已存在该协议类型设备，请手动检查".format(self.ip))
                self.result = u"设备{0}:NVR通道中已存在该协议类型设备，请手动检查".format(self.ip)
                return False
            else:
                return True
        except Exception as e:
            print(e)

            return False

    # 添加设备
    def add_device(self):
        try:
            for i in range(1,self.channel+1):
                put_text = xmltodict.parse(nvr_add_xml)
                if self.protocol == u'HIKVISION' or self.protocol == u'HIKVISION增强':
                    put_text[u'InputProxyChannel'][u'sourceInputPortDescriptor'][u'proxyProtocol'] = 'HIKVISION'
                else:
                    put_text[u'InputProxyChannel'][u'sourceInputPortDescriptor'][u'proxyProtocol'] = 'ONVIF'
                put_text[u'InputProxyChannel'][u'sourceInputPortDescriptor'][u'ipAddress'] = self.ip
                put_text[u'InputProxyChannel'][u'sourceInputPortDescriptor'][u'managePortNo'] = self.nvr_port
                put_text[u'InputProxyChannel'][u'sourceInputPortDescriptor'][u'userName'] = self.device_username
                put_text[u'InputProxyChannel'][u'sourceInputPortDescriptor'][u'password'] = self.device_password
                if self.protocol == u'HIKVISION增强':
                    put_text[u'InputProxyChannel'][u'certificateValidationEnabled'] = 'true'
                put_text[u'InputProxyChannel'][u'sourceInputPortDescriptor'][u'srcInputPort'] = str(i)
                put_text = xmltodict.unparse(put_text)
                put = requests.post(u'http://{0}:{1}{2}'.format(self.nvr_ip, self.port, nvr_add_url),data=put_text,
                                   auth=HTTPDigestAuth(self.nvr_username, self.nvr_password), timeout=6)
                put.raise_for_status()
            return True
        except Exception as e:
            print(e)
            print(u"设备{0}:通道{1}添加至NVR失败".format(self.ip,str(i)))
            self.result = u"设备{0}:通道{1}添加至NVR失败".format(self.ip,str(i))
            return False

    # 开启Onvif
    def open_onvif(self):
        n = 0
        while True:
            try:
                n += 1
                get = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, onvif_url),
                                   auth=HTTPDigestAuth(self.device_username, self.device_password), timeout=6)
                get_text = xmltodict.parse(get.text)
                get_text['Integrate']['ONVIF']['enable'] = 'true'
                put_text = xmltodict.unparse(get_text)
                put = requests.put('http://{0}:{1}{2}'.format(self.ip, self.port, onvif_url),
                                   data=put_text,
                                   auth=HTTPDigestAuth(self.device_username, self.device_password), timeout=6)
                put.raise_for_status()
                return True
            except Exception as e:
                if n >= 3:
                    print(e)
                    print(u"设备{0}:开启ONVIF失败".format(self.ip))
                    self.result = u"设备{0}:开启ONVIF失败".format(self.ip)
                    return False

    # 创建Onvif用户
    def create_account(self):
        n = 0
        get = requests.get('http://%s:%s' % (self.ip, self.port) + '/ISAPI/Security/ONVIF/users?security=0',
                           auth=HTTPDigestAuth(self.device_username, self.device_password), timeout=10)
        if 'admin' in get.text:
            return True
        while True:
            try:
                n += 1
                put = requests.put('http://%s:%s' % (self.ip, self.port) + onvif_account_url, data=onvif_user_url,
                                   auth=HTTPDigestAuth(self.device_username, self.device_password), timeout=10)
                put.raise_for_status()
                return True
            except Exception as e:
                if n >= 3:
                    print(e)
                    print(u"设备{0}:创建ONVIF用户失败".format(self.ip))
                    self.result = u"设备{0}:创建ONVIF用户失败".format(self.ip)
                    return False

    # NVR配置GB28181
    def nvr_gb28181(self):
        try:
            put = requests.put('http://{0}:{1}{2}'.format(self.nvr_ip, self.port, nvr_gb28181_url),
                                   data=nvr_gb28181_xml,
                                   auth=HTTPDigestAuth(self.nvr_username, self.nvr_password), timeout=10)
            put.raise_for_status()
            if 'rebootRequired' in put.text:
                reboot = requests.put('http://{0}:{1}{2}'.format(self.nvr_ip, self.port, reboot_url),
                                      auth=HTTPDigestAuth(self.nvr_username, self.nvr_password), timeout=100)
                reboot.raise_for_status()
            return True
        except Exception as e:
            print(u"NVR{0}：开启GB28181服务失败".format(self.nvr_ip))
            self.result = u"NVR{0}：开启GB28181服务失败".format(self.nvr_ip)
            return False

    # 设备配置GB28181
    def gb28181(self):
        try:
            get = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, gb28181_url),
                                   auth=HTTPDigestAuth(self.device_username, self.device_password), timeout=10)
            get.raise_for_status()
            get_text = xmltodict.parse(get.text)
            get_text['SIPServerList']['SIPServer']['GB28181']['enabled'] = 'true'
            get_text['SIPServerList']['SIPServer']['GB28181']['registrar'] = self.nvr_ip
            get_text['SIPServerList']['SIPServer']['GB28181']['registrarPort'] = '5061'
            get_text['SIPServerList']['SIPServer']['GB28181']['password'] = 'abcd1234'
            put_text = xmltodict.unparse(get_text)
            put = requests.put('http://{0}:{1}{2}'.format(self.ip, self.port, gb28181_url), data=put_text,
                               auth=HTTPDigestAuth(self.device_username, self.device_password), timeout=10)
            put.raise_for_status()
            return True
        except Exception as e:
            print(u"设备{0}:开启GB28181失败".format(self.ip))
            self.result = u"设备{0}:开启GB28181失败".format(self.ip)
            return False

    # 增强型HIKVISION配置
    def cert_export(self):
        try:
            headers = {"Content-Type": "application/x-x509-ca-cert"}
            get = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, cert_url),
                                   auth=HTTPDigestAuth(self.device_username, self.device_password), timeout=10)
            get.raise_for_status()
            put = requests.put('http://{0}:{1}{2}'.format(self.nvr_ip, self.port, nvr_cert_url),headers=headers,data=get.content,
                                   auth=HTTPDigestAuth(self.nvr_username, self.nvr_password), timeout=10)
            if '<subStatusCode>certificateAlreadyExist</subStatusCode>' in put.text:
                return True
            elif '<subStatusCode>ok</subStatusCode>' in put.text:
                return True
            else:
                print(u"设备{0}:证书导入NVR失败".format(self.ip))
                self.result = u"设备{0}:证书导入NVR失败".format(self.ip)
                return False
        except Exception as e:
            print(e)
            print(u"设备{0}:证书导入NVR失败".format(self.ip))
            self.result = u"设备{0}:证书导入NVR失败".format(self.ip)
            return False


    def test(self):
        try:
            if self.check_channels():
                if self.modify_channelName():
                    if self.check_nvr():
                        if self.protocol == 'ONVIF':
                            if self.create_account():
                                if self.open_onvif():
                                    if self.add_device():
                                        print(u"设备{0}:导入NVR成功".format(self.ip))
                        elif self.protocol == 'HIKVISION':
                            if self.add_device():
                                print(u"设备{0}:导入NVR成功".format(self.ip))
                        elif self.protocol == 'GB28181':
                            if self.nvr_gb28181():
                                if self.gb28181():
                                    print(u"设备{0}:导入NVR成功".format(self.ip))
                        else:
                            if self.cert_export():
                                if self.add_device():
                                    print(u"设备{0}:导入NVR成功".format(self.ip))
        except Exception as e:
                    print(u"设备{0}:导入NVR失败".format(self.ip))


# 读取Excel信息
class Excel:

    # 初始化
    def __init__(self):
        self.filename = 'devices/devices.xlsx'  # 读取的文件名
        self.ip = []                            # 设备IP
        self.device_username = []               # 设备用户名
        self.device_password = []               # 设备密码
        self.nvr_ip = []                        # nvr地址
        self.nvr_username = []               # 设备用户名
        self.nvr_password = []               # 设备密码
        self.protocol = []                      # 协议

    def read(self):
        # 读取Excel
        try:
            data = openpyxl.load_workbook(self.filename)

            # 读取Sheet1表
            read = data[u'批量导入NVR']
            # 获取设备IP与格式化次数
            self.ip = list(filter(None, getColValues(read, 1)))[1:]               # 设备地址
            self.device_username = list(filter(None, getColValues(read, 2)))[1:]  # 设备用户名
            self.device_password = list(filter(None, getColValues(read, 3)))[1:]  # 设备密码
            self.nvr_ip = list(filter(None, getColValues(read, 4)))[1:]           # nvr地址
            self.nvr_username = list(filter(None, getColValues(read, 5)))[1:]     # 设备用户名
            self.nvr_password = list(filter(None, getColValues(read, 6)))[1:]     # 设备密码
            self.protocol = list(filter(None, getColValues(read, 7)))[1:]         # 协议
            return True
        except Exception as e:
            print(e)
            return False

# 从读取到生成报告总流程
def NVR_ADD():
    try:
        print(u'开始执行')
        result_r = []
        excel = Excel()
        if excel.read():
            nums = len(excel.ip)
            for i in range(nums):
                t = Device(excel.ip[i], excel.device_username[i], excel.device_password[i], excel.nvr_ip[i],excel.nvr_username[i], excel.nvr_password[i],excel.protocol[i])
                t.test()
                result_r.append(t.result)
            return result_r
        print(u'执行结束')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    A = Device('10.65.71.155', 'admin', 'abcd1234', '10.65.153.100','admin', 'abcd1234', 'GB28181')
    A.cert_export()