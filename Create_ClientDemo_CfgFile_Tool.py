# -*- coding: utf-8 -*-
import json
import openpyxl
import collections
from public_function import getColValues


class Excel:

    # 初始化
    def __init__(self):
        self.filename = 'devices/devices.xlsx'
        self.ip = []
        self.count = []

    def read(self):
        # 读取Excel
        try:
            data = openpyxl.load_workbook(self.filename)

            StreamType = [u'主码流（录像）', u'子码流（网传）', u'码流三', u'转码码流/码流四', u'码流五']
            LinkMode = [u'TCP', u'UDP', u'MCAST', u'RTP', u'RTP over RTSP', u'RTP over HTTP', u'HRUDP']
            PreviewMode = [u'正常预览', u'延时预览']
            PreviewProtocolType = [u'私有协议', u'RTSP协议']

            # 读取Sheet表
            read = data[u"ClientDemo配置文件生成"]

            # 获取填写的参数
            self.ChanID = list(filter(None, getColValues(read, 1)))[2:]
            self.DeviceIP = list(filter(None, getColValues(read, 2)))[2:]
            self.DevicePort = list(filter(None, getColValues(read, 3)))[2:]
            self.LoginUserName = list(filter(None, getColValues(read, 4)))[2:]
            self.LoginUserPwd = list(filter(None, getColValues(read, 5)))[2:]
            self.LocalNodeName = list(filter(None, getColValues(read, 6)))[2:]
            self.StreamType_old = list(filter(None, getColValues(read, 7)))[2:]
            self.support = read.cell(row=2,column=11).value

            # 判断码流类型
            self.StreamType = []
            for i in self.StreamType_old:
                if i in StreamType:
                    self.StreamType.append(StreamType.index(i))

            # 判断取流协议
            self.LinkMode_old = list(filter(None, getColValues(read, 8)))[2:]
            self.LinkMode = []
            for i in self.LinkMode_old:
                if i in LinkMode:
                    self.LinkMode.append(LinkMode.index(i))

            # 判断预览模式
            self.PreviewMode_old = list(filter(None, getColValues(read, 9)))[2:]
            self.PreviewMode = []
            for i in self.PreviewMode_old:
                if i in PreviewMode:
                    self.PreviewMode.append(PreviewMode.index(i))

            # 判断预览协议
            self.PreviewProtocolType_old = list(filter(None, getColValues(read, 10)))[2:]
            self.PreviewProtocolType = []
            for i in self.PreviewProtocolType_old:
                if i in PreviewProtocolType:
                    self.PreviewProtocolType.append(PreviewProtocolType.index(i))

            # 获取的信息汇总
            self.device = []
            for i in range(len(self.DeviceIP)):
                d = [self.DeviceIP[i],self.DevicePort[i],self.LoginUserName[i],
                          self.LoginUserPwd[i],self.LocalNodeName[i],
                          self.StreamType[i],self.LinkMode[i],self.PreviewMode[i],
                          self.PreviewProtocolType[i],i,self.ChanID[i]-1]
                self.device.append(d)
            return True
        except Exception as e:
            print(e)
            return False

    # 写入
    def write(self, device):
        # 按照指定的Json格式写入
        data_device = collections.OrderedDict()
        data_device['ID'] = device[9]
        data_device['SerialNumber'] = "DS-2DF7286-A20140902CCCH478174537B"
        data_device['ChannelNumber'] = 1
        data_device['StartChannel'] = 1
        data_device['AlarmInNum'] = 7
        data_device['AlarmOutNum'] = 2
        data_device['IPChanNum'] = 0
        data_device['MirrorChanNum'] = 0
        data_device['StartMirrorChanNo'] = 0
        data_device['LocalNodeName'] = device[4]
        data_device['DeviceType'] = 41
        data_device['DiskNum'] = 0
        data_device['LoginUserName'] = device[2]
        data_device['LoginUserPwd'] = device[3]
        data_device['DeviceIP'] = device[0]
        data_device['DeviceMultiIP'] = "230.0.0.1"
        data_device['DevicePort'] = device[1]
        data_device['DeviceName'] = "DS-2DF7286-A"
        data_device['LoginMode'] = 0
        if device[1] == 8443:
            data_device['Https'] = 1
        else:
            data_device['Https'] = 0
        data_channel = collections.OrderedDict()
        data_channel['ChanID'] = device[10]
        data_channel['DeviceIndex'] = 0
        data_channel['ChanIndex'] = 0
        data_channel['ChanName'] = "Camera1"
        data_channel['Protocol'] = 0
        data_channel['PicResolution'] = 0
        data_channel['PicQuality'] = 0
        data_channel['Enable'] = 1
        data_channel['PreviewMode'] = device[7]
        data_channel['PreviewProtocolType'] = device[8]
        data_channel['VideoCodingType'] = 0
        data_channel['StreamType'] = device[5]
        data_channel['LinkMode'] = device[6]
        ddd = []
        ddd.append(data_channel)
        data_device["Channels"] = ddd
        return data_device

    # 多通道处理
    def handle(self,data):
        datadata = data

        # 列表C：将填写的相同IP汇总在一起
        B = list(dict.fromkeys(self.DeviceIP))
        C = [] #
        for i in B:
            D = []
            for j in range(len(self.DeviceIP)):
                if self.DeviceIP[j] == i:
                    D.append(j)
            C.append(D)

        # 列表D：多通道设备
        D = []
        for i in C:
            if len(i) > 1:
                D.append(i)

        # 多通道设备Json修改
        for i in D:
            E = []
            for j in i:
                E.append(datadata['Devices'][j]['Channels'][0])
            datadata['Devices'][i[0]]['Channels'] = E

        # 将多通道设备合一，多余的Json描述删除
        removelist = []
        for i in D:
            for j in i[1:]:
                removelist.append(j)
        new_list = [datadata['Devices'][i] for i in range(len(datadata['Devices'])) if i not in removelist]
        datadata['Devices'] = new_list
        return datadata

# 总逻辑流程
def Client():
    print(u'开始执行!!')
    A = Excel()
    A.read()
    datadata = collections.OrderedDict()
    data = []
    for i in A.device:
        data.append(A.write(i))
    datadata['Devices'] = data
    if A.support == 'T':
        datadata = A.handle(datadata)
    output = json.dumps(datadata, indent=4, separators=(',', ': '))
    filename = 'devices/DeviceCfg.json'
    with open(filename, 'w') as file:
        file.write(output)
    print(u'执行完毕!!')


if __name__ == '__main__':
    Client()