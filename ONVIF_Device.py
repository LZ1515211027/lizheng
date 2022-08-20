# -*- coding: utf-8 -*-
import requests
from requests.auth import HTTPDigestAuth
import xmltodict
import re
import time
from datetime import datetime
from variable import *
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
    def __init__(self, ip, username, password, nas_address='', nas_file_path='', restore_choose='T', record_channel='1'):
        self.ip = ip  # 设备ip地址
        self.port = '80'  # 设备HTTP端口号
        self.username = username  # 帐户名
        self.password = password  # 密码
        self.nas_address = nas_address  # nas地址
        self.nas_file_path = nas_file_path  # nas文件路径
        self.restore_choose = restore_choose # 是否简单恢复
        self.record_channel = record_channel # 录像通道
        self.storage = 'sd' if nas_address == '' else 'nas' # 格式化SD卡或NAS

        self.channels = [] # 设备通道数
        self.audio = '' # 是否支持音频
        self.videostream = 0 # 码流数

        # 各个配置项的执行结果
        self.restore_result = ''
        self.dst_result = ''
        self.checktime_result = ''
        self.change_video_result = []
        self.ipv6_result = ''
        self.https_result = ''
        self.wdr_result = []
        self.onvif_result = ''
        self.account_result = ''
        self.storage_result = u'未执行'
        self.record_result = u'未执行'
        self.result = []

    # 简单恢复
    def restore(self):
        # 判断是否选择了简单恢复T
        if self.restore_choose == 'T':
            n = 0
            while True:
                try:
                    n += 1
                    put = requests.put('http://{0}:{1}{2}'.format(self.ip, self.port, restore_url),
                                       auth=HTTPDigestAuth(self.username, self.password), timeout=30)
                    put.raise_for_status()
                    print(u'设备开始简单恢复')
                    time.sleep(50)
                    if self.check_status():
                        self.restore_result = 'Pass'
                        return True
                    else:
                        self.restore_result = u'设备未上线'
                        return False
                except Exception as e:
                    if n >= 3:
                        print(e)
                        print(u"简单恢复失败")
                        self.restore_result = 'Failed'
                        return False
        else:
            print(u"不执行简单恢复")
            self.restore_result = u'不执行'
            return True

    # 检查设备是否在线
    def check_status(self):
        n = 0
        while True:
            try:
                n += 1
                put = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, check_status_url),
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=10)
                put.raise_for_status()
                print(u"设备上线成功")
                return True
            except Exception as e:
                if n >= 48:
                    print(e)
                    print(u"检测到设备长达8分钟没有上线！")
                    return False

    # 登录设备
    def check(self):
        n = 0
        while True:
            try:
                n += 1
                get = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, check_status_url),
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                get.raise_for_status()
                print(u"设备登录成功")
                return True
            except Exception as e:
                if n >= 2:
                    print(e)
                    print(u"登录设备失败！")
                    return False

    # 获取通道数
    def check_channels(self):
        n = 0
        channels = 0
        while True:
            try:
                n += 1
                get = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, channel_url),
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                get.raise_for_status()

                # 报文中遍历指定节点，获取通道数
                root = etree.XML(get.text.encode('utf-8'))
                VideoInputChannels = root.xpath("//*[local-name()='VideoInputChannel']")
                for _ in VideoInputChannels:
                    channels += 1
                    self.channels.append(str(channels))

                print(u"设备通道数为{0}".format(self.channels[-1]))
                return True
            except Exception as e:
                if n >= 2:
                    print(e)
                    print(u"获取通道数失败")
                    return False

    # 关闭夏令时
    def dst_close(self):
        try:
            # 查询设备是否支持夏令时
            cap = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, dst_cap_url),
                               auth=HTTPDigestAuth(self.username, self.password), timeout=5)
            if 'true</isSupportDst>' in cap.text:
                n = 0
                while True:
                    try:
                        n += 1
                        get = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, time_url),
                                           auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                        get_text = xmltodict.parse(get.text)
                        check = get_text['Time']['timeZone']

                        if 'DST' in check:
                            # 通过修改设备时间设置，达到关闭夏令时的目的
                            get_text['Time']['timeZone'] = check[0:check.index('D')]
                            put_text = xmltodict.unparse(get_text)
                            put = requests.put('http://{0}:{1}{2}'.format(self.ip, self.port, time_url),
                                               data=put_text,
                                               auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                            put.raise_for_status()
                            print(u"关闭夏令时成功")
                            self.dst_result = 'Pass'
                            return True
                        else:
                            print(u"关闭夏令时成功")
                            self.dst_result = 'Pass'
                            return True
                    except Exception as e:
                        if n >= 3:
                            print(e)
                            print(u"关闭夏令时失败")
                            self.dst_result = 'Failed'
                            return False
            else:
                print(u"设备不支持夏令时")
                self.dst_result = u'设备不支持'
                return True
        except Exception as e:
            print(e)
            self.dst_result = u'获取夏令时能力失败'
            return False

    # 设备校时
    def check_time(self):
        # 获取计算机当前时间
        now_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
        n = 0
        while True:
            try:
                n += 1
                get = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, checktime_url),
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                get_text = xmltodict.parse(get.text)
                get_text['Time']['localTime'] = now_time
                get_text['Time']['timeZone'] = 'CST-8:00:00'
                put_text = xmltodict.unparse(get_text)
                put = requests.put('http://{0}:{1}{2}'.format(self.ip, self.port, checktime_url),
                                   data=put_text,
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                put.raise_for_status()
                print(u'校时成功')
                self.checktime_result = 'Pass'
                return True
            except Exception as e:
                if n >= 3:
                    print(e)
                    print(u"校时失败")
                    self.checktime_result = 'Failed'
                    return False

    # 获取设备音频能力
    def check_audio_stream(self, channel):
        n = 0
        while True:
            try:
                n += 1
                stream_capabilities = requests.get(u'http://{0}:{1}{2}'.format(self.ip, self.port, video_audio_url+channel+u'01/capabilities'),
                                                   auth=HTTPDigestAuth(self.username, self.password))
                stream_capabilities.raise_for_status()
                capabilities_text = xmltodict.parse(stream_capabilities.text)
                stream = capabilities_text[u'StreamingChannel']
                if u'Audio' in stream:
                    print(u"通道{0}支持复合流".format(channel))
                    self.audio = 'true'
                    return True
                else:
                    print(u"通道{0}不支持复合流".format(channel))
                    self.audio = 'false'
                    return False
            except Exception as e:
                if n >= 3:
                    print(e)
                    print(u"通道{0}获取音频能力失败".format(channel))
                    self.audio = 3
                    return 3

    # 获取设备视频能力
    def check_video_stream(self, channel):
        n = 0
        while True:
            try:
                n += 1
                stream_capabilities = requests.get(u'http://{0}:{1}{2}'.format(self.ip, self.port, video_audio_url+channel+u'01/capabilities'),
                                                   auth=HTTPDigestAuth(self.username, self.password))
                stream_capabilities.raise_for_status()
                capabilities_text = xmltodict.parse(stream_capabilities.text)
                stream = capabilities_text[u'StreamingChannel'][u'id'][u'@opt'].split(',')
                self.videostream = len(stream)
                print(u"通道{0}支持{1}个码流".format(channel, self.videostream))
                return True
            except Exception as e:
                if n >= 3:
                    print(e)
                    print(u"通道{0}获取视频能力失败".format(channel))
                    self.videostream = 'False'
                    return False

    # 更改设备视频参数
    def change_video(self, channel):
        self.check_video_stream(channel)
        self.check_audio_stream(channel)
        if self.videostream == 'False':
            print(u"通道{0}未能获取到设备码流数，请手动配置".format(channel))
            self.change_video_result.append(u'通道{0}未能获取到设备码流数，请手动配置'.format(channel))
            return False
        if self.audio == 3:
            print(u'通道{0}未能获取到音频能力，请手动配置'.format(channel))
            self.change_video_result.append(u'通道{0}未能获取到音频能力，请手动配置'.format(channel))
            return False
        num = 0
        while True:
            try:
                num += 1
                for i in range(self.videostream):
                    n = str(i + 1)
                    capabilities = requests.get(u'http://{0}:{1}{2}'.format(self.ip, self.port, video_audio_url + channel
                                                                           + '0'+ n +u'/capabilities'),
                                                auth=HTTPDigestAuth(self.username, self.password))

                    # 通过协议获取到当前码流支持的最小分辨率
                    capabilities_text = xmltodict.parse(capabilities.text)
                    videoResolutionWidth = \
                        capabilities_text[u'StreamingChannel'][u'Video'][u'videoResolutionWidth'][u'@opt'].split(',')[0]
                    videoResolutionHeight = \
                        capabilities_text[u'StreamingChannel'][u'Video'][u'videoResolutionHeight'][u'@opt'].split(',')[0]

                    # 获取设备当前指定码流的分辨率
                    get = requests.get(u'http://{0}:{1}{2}'.format(self.ip, self.port, video_audio_url + channel
                                                                  + '0' + n),
                                       auth=HTTPDigestAuth(self.username, self.password))
                    get_text = xmltodict.parse(get.text)

                    # 修改当前码流的分辨率和视频类型
                    get_text[u'StreamingChannel'][u'Video'][u'videoResolutionWidth'] = videoResolutionWidth
                    get_text[u'StreamingChannel'][u'Video'][u'videoResolutionHeight'] = videoResolutionHeight
                    get_text[u'StreamingChannel'][u'Video'][u'GovLength'] = 1
                    if self.audio == 'true':
                        get_text[u'StreamingChannel'][u'Audio'][u'enabled'] = self.audio
                    put_text = xmltodict.unparse(get_text)
                    put = requests.put(u'http://{0}:{1}{2}'.format(self.ip, self.port, video_audio_url + channel
                                                                  + '0' + n), data=put_text,
                                       auth=HTTPDigestAuth(self.username, self.password))
                    put.raise_for_status()
                    print(u'通道{0}的码流{1}修改视频参数成功'.format(channel, n))
                self.change_video_result.append(u'Pass')
                return True
            except Exception as e:
                if num >= 3:
                    print(e)
                    print(u'通道{0}的码流{1}修改视频参数失败'.format(channel, n))
                    self.change_video_result.append(u'Failed')
                    return False

    # 设置IPV6模式为路由公告
    def open_ipv6(self):
        # 判断设备是否支持IPV6
        cap = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, ipv6_cap_url),
                           auth=HTTPDigestAuth(self.username, self.password), timeout=5)
        if '</Ipv6Mode>' in cap.text:
            n = 0
            while True:
                try:
                    n += 1
                    network = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, network_url),
                                           auth=HTTPDigestAuth(self.username, self.password))
                    network_text = xmltodict.parse(network.text)
                    network_text['NetworkInterface']['IPAddress']['Ipv6Mode']['ipV6AddressingType'] = 'ra'
                    put_text = xmltodict.unparse(network_text)
                    put = requests.put('http://{0}:{1}{2}'.format(self.ip, self.port, network_url),
                                       data=put_text,
                                       auth=HTTPDigestAuth(self.username, self.password))
                    put.raise_for_status()
                    print(u"开启路由公告成功")
                    self.ipv6_result = 'Pass'
                    return True
                except Exception as e:
                    if n >= 3:
                        print(e)
                        print(u"开启路由公告失败")
                        self.ipv6_result = 'Failed'
                        return False
        else:
            print(u"设备不支持IPV6")
            self.ipv6_result = u'不支持IPV6'
            return False

    # 关闭HTTPS
    def close_https(self):
        # 判断设备是否支持HTTPS
        cap = requests.get(u'http://{0}:{1}{2}'.format(self.ip, self.port, https_cap_url),
                           auth=HTTPDigestAuth(self.username, self.password))
        if u'true</isSupportHttps>' in cap.text:
            n = 0
            while True:
                try:
                    n += 1
                    get = requests.get(u'http://{0}:{1}{2}'.format(self.ip, self.port, https_url),
                                       auth=HTTPDigestAuth(self.username, self.password))
                    get_text = xmltodict.parse(get.text)
                    get_text[u'AdminAccessProtocol'][u'enabled'] = 'false'
                    put_text = xmltodict.unparse(get_text)
                    put = requests.put(u'http://{0}:{1}{2}'.format(self.ip, self.port, https_url),
                                       data=put_text,
                                       auth=HTTPDigestAuth(self.username, self.password))
                    put.raise_for_status()
                    print(u'关闭https成功')
                    self.https_result = u'Pass'
                    return True
                except Exception as e:
                    if n >= 3:
                        print(e)
                        print(u"关闭https失败")
                        self.https_result = u'Failed'
                        return False
        else:
            print(u"设备不支持HTTPS")
            self.https_result = u'不支持HTTPS'
            return False

    # 场景模式切换至背光模式
    def change_scene(self, channel, scene):
        n = 0
        while True:
            try:
                n += 1
                get = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, scene_url+channel+'/mountingScenario'),
                                   auth=HTTPDigestAuth(self.username, self.password))
                get_text = xmltodict.parse(get.text)
                get_text['MountingScenario']['mode'] = scene
                put_text = xmltodict.unparse(get_text)
                put = requests.put('http://{0}:{1}{2}'.format(self.ip, self.port, scene_url+channel+'/mountingScenario'),
                                   data=put_text,
                                   auth=HTTPDigestAuth(self.username, self.password))
                put.raise_for_status()
                print(u'通道{0}场景切换至{1}模式成功'.format(channel, scene))
                return True
            except Exception as e:
                if n >= 3:
                    print(e)
                    print(u'通道{0}场景切换至{1}失败'.format(channel, scene))
                    return False

    # 关闭背光场景下的WDR
    def close_wdr(self, channel):
        # 判断设备是否支持WDR
        cap = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, wdr_cap_url+channel+'/capabilities'),
                           auth=HTTPDigestAuth(self.username, self.password))
        if '</WDR>' in cap.text:
            # 判断设备是否支持背光场景
            scene_cap = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, scene_url+channel+'/mountingScenario/capabilities'),
                                     auth=HTTPDigestAuth(self.username, self.password))
            if 'backlight' in scene_cap.text:
                scene_text = xmltodict.parse(scene_cap.text)
                # 保存设备当前场景信息
                self.scene = scene_text['MountingScenario']['mode']['#text']
                if self.change_scene(channel, 'backlight'):
                    n = 0
                    while True:
                        try:
                            n += 1
                            get = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, wdr_url+channel+'/WDR'),
                                               auth=HTTPDigestAuth(self.username, self.password))
                            get_text = xmltodict.parse(get.text)
                            get_text['WDR']['mode'] = 'close'
                            put_text = xmltodict.unparse(get_text)
                            put = requests.put('http://{0}:{1}{2}'.format(self.ip, self.port, wdr_url+channel+'/WDR'),
                                               data=put_text,
                                               auth=HTTPDigestAuth(self.username, self.password))
                            put.raise_for_status()
                            # 切换回设备原来的场景
                            if self.change_scene(channel, self.scene):
                                print(u"通道{0}关闭WDR成功".format(channel))
                                self.wdr_result.append('Pass')
                                return True
                            else:
                                print(u"通道{0}关闭WDR成功，但切换回原场景失败".format(channel))
                                self.wdr_result.append('Failed')
                                return False
                        except Exception as e:
                            if n >= 3:
                                print(e)
                                print(u"通道{0}关闭WDR失败".format(channel))
                                self.wdr_result.append('Failed')
                                return False
                else:
                    self.wdr_result.append('Failed')
                    return False
            else:
                print(u"通道{0}不支持背光场景".format(channel))
                self.wdr_result.append(u'不支持背光场景')
                return True
        else:
            print(u"通道{0}不支持WDR".format(channel))
            self.wdr_result.append(u'不支持WDR')
            return True

    # 开启Onvif
    def open_onvif(self):
        n = 0
        while True:
            try:
                n += 1
                get = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, onvif_url),
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                get_text = xmltodict.parse(get.text)
                get_text['Integrate']['ONVIF']['enable'] = 'true'
                put_text = xmltodict.unparse(get_text)
                put = requests.put('http://{0}:{1}{2}'.format(self.ip, self.port, onvif_url),
                                   data=put_text,
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                put.raise_for_status()
                print(u"开启Onvif成功")
                self.onvif_result = 'Pass'
                return True
            except Exception as e:
                if n >= 3:
                    print(e)
                    print(u"开启onvif失败")
                    self.onvif_result = 'Failed'
                    return False

    # 创建Onvif用户
    def create_account(self):
        n = 0
        get = requests.get('http://%s:%s' % (self.ip, self.port) + '/ISAPI/Security/ONVIF/users?security=0',
                           auth=HTTPDigestAuth(self.username, self.password), timeout=5)
        if 'admin' in get.text:
            print(u"ONVIF已存在admin账户")
            self.account_result = 'Pass'
            return True
        while True:
            try:
                n += 1
                put = requests.put('http://%s:%s' % (self.ip, self.port) + onvif_account_url, data=onvif_user_url,
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=10)
                put.raise_for_status()
                print(u'创建admin账户成功')
                self.account_result = 'Pass'
                return True
            except Exception as e:
                if n >= 3:
                    print(e)
                    print(u"创建admin账户失败")
                    self.account_result = 'Failed'
                    return False

    # 添加nas盘
    def nas(self):
        if self.storage == 'nas':
            n = 0
            while True:
                try:
                    get_text = xmltodict.parse(nas_xml)
                    get_text['nasList']['nas']['ipAddress'] = self.nas_address
                    get_text['nasList']['nas']['path'] = self.nas_file_path
                    put_text = xmltodict.unparse(get_text)
                    put = requests.put('http://%s:%s' % (self.ip, self.port) + nas_url, data=put_text,
                                       auth=HTTPDigestAuth(self.username, self.password), timeout=150)
                    put.raise_for_status()
                    print(u"挂载NAS盘成功")
                    print(u"查看NAS盘状态")
                    while True:
                        n += 1
                        print(u"等待15秒")
                        time.sleep(15)
                        get = requests.get('http://%s:%s' % (self.ip, self.port) + storage_url,
                                           auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                        get_text1 = xmltodict.parse(get.text)
                        check = get_text1['storage']['nasList']['nas']['status']
                        if check == 'ok' or check == 'error' or check == 'unformatted':
                            print(u'挂载nas盘成功')
                            return True
                        elif check == 'initializing':
                            print(u"nas盘正在初始化中")
                            continue
                        if n >= 10:
                            print(u"挂载nas盘失败")
                            self.storage_result = u'挂载nas盘失败'
                            return False
                except Exception as e:
                    print(e)
                    print(u"挂载nas盘失败")
                    self.storage_result = u'挂载nas盘失败'
                    return False
        else:
            return True

    # 格式化SD卡
    def format_storage(self):
        # 格式化前先关闭录像计划
        if self.record('false'):
            n = 0
            # 判断设备存储介质为NAS还是SD卡
            if self.storage == 'sd':
                while True:
                    try:
                        n += 1
                        get = requests.get('http://%s:%s' % (self.ip, self.port) + storage_url,
                                           auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                        get_text = xmltodict.parse(get.text)
                        sd_status = get_text['storage']['hddList']
                        if 'hdd' not in sd_status:
                            print(u'未识别到SD卡')
                            self.storage_result = u'未识别到SD卡'
                            return False
                        print(u'sd卡开始格式化')
                        put = requests.put('http://%s:%s' % (self.ip, self.port) + format_url,
                                           auth=HTTPDigestAuth(self.username, self.password), timeout=600)
                        put.raise_for_status()
                        print(u'sd卡格式化成功')
                        self.storage_result = 'Pass'
                        return True
                    except Exception as e:
                        if n >= 2:
                            print(e)
                            print(u"sd卡格式化失败")
                            self.storage_result = 'Failed'
                            return False
            else:
                while True:
                    try:
                        n += 1
                        print(u'nas盘正在格式化')
                        put = requests.put('http://%s:%s' % (self.ip, self.port) + nas_format_url,
                                           auth=HTTPDigestAuth(self.username, self.password), timeout=600)
                        put.raise_for_status()
                        print(u'nas盘格式化成功')
                        self.storage_result = 'Pass'
                        return True
                    except Exception as e:
                        if n >= 2:
                            print(e)
                            print(u"nas盘格式化失败")
                            self.storage_result = 'Failed'
                            return False
        else:
            print(u'关闭录像计划失败，不进行格式化')
            self.storage_result = u'关闭录像计划失败，不进行格式化'
            return False

    # 更改录像计划状态
    def record(self, status):
        n = 0
        while True:
            try:
                n += 1
                get = requests.get('http://%s:%s' % (self.ip, self.port) + record_url + self.record_channel +'01',
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                get_text = xmltodict.parse(get.text)
                get_text['Track']['CustomExtensionList']['CustomExtension']['enableSchedule'] = status
                put_text = xmltodict.unparse(get_text)
                put = requests.put('http://%s:%s' % (self.ip, self.port) + record_url + self.record_channel +'01', data=put_text,
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                put.raise_for_status()
                if status == 'true':
                    print(u"开启通道{0}录像计划成功".format(self.record_channel))
                else:
                    print(u"关闭通道{0}录像计划成功".format(self.record_channel))
                return True
            except Exception as e:
                if n >= 3:
                    print(e)
                    if status == 'true':
                        print(u"开启通道{0}录像计划失败".format(self.record_channel))
                    else:
                        print(u"关闭通道{0}录像计划失败".format(self.record_channel))
                    return False

    # 配置7*24小时全天定时录像计划
    def record_plan(self):
        n = 0
        while True:
            try:
                n += 1
                get = requests.get('http://%s:%s' % (self.ip, self.port) + record_url + self.record_channel +'01',
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                get_text = get.text
                a = re.search("<TrackSchedule>", get_text).span()
                b = re.search("</TrackSchedule>", get_text).span()
                check = [a[1], b[0]]
                get_text = get_text.replace(get_text[check[0]:check[1]], allday_url)
                put = requests.put('http://%s:%s' % (self.ip, self.port) + record_url + self.record_channel +'01', data=get_text,
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                put.raise_for_status()
                print(u"全天录像计划配置成功")
                if self.record('true'):
                    print(u'开始录像2分钟')
                    time.sleep(118)
                    print(u'已录好2分钟的录像')

                    # 关闭录像计划
                    self.record('false')
                    self.record_result = 'Pass'
                    return True
                else:
                    print(u'开启录像计划失败，未能进行录像')
                    self.record_result = 'Failed'
            except Exception as e:
                if n >= 3:
                    print(e)
                    print(u"全天录像计划配置失败")
                    self.record_result = 'Failed'
                    return False

    # 运行主函数
    def test(self):
        try:
            assert self.restore()         # 简单恢复
            assert self.check_channels()  # 获取通道数
            self.dst_close()              # 关闭夏令时
            self.check_time()             # 设备校时
            self.open_ipv6()              # 设置IPV6模式为路由公告
            self.close_https()            # 关闭HTTPS
            self.open_onvif()             # 开启Onvif
            self.create_account()         # 创建Onvif用户
            for i in self.channels:
                self.close_wdr(i)         # 关闭背光场景下的WDR

            for channel in self.channels:
                assert self.change_video(channel)    # 更改设备视音频参数

            assert self.nas()             # 挂载nas盘
            assert self.format_storage()  # 格式化存储介质
            self.record_plan()            # 录像2分钟
            self.result = [self.restore_result, self.dst_result, self.checktime_result, self.change_video_result,
                           self.ipv6_result, self.https_result, self.wdr_result, self.onvif_result, self.account_result,
                           self.storage_result, self.record_result]
            return True
        except Exception as e:
            print(e)
            self.result = [self.restore_result, self.dst_result, self.checktime_result, self.change_video_result,
                           self.ipv6_result, self.https_result, self.wdr_result, self.onvif_result, self.account_result,
                           self.storage_result, self.record_result]
            print(u"工具执行失败")
            return False

if __name__ == '__main__':
    A = Device('10.65.71.152', 'admin', 'abcd1234', nas_address='', nas_file_path='', restore_choose='F', record_channel='1')
    A.open_onvif()