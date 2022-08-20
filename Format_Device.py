# -*- coding: utf-8 -*-
import requests                           # 请求相关的库
from requests.auth import HTTPDigestAuth  # 摘要认证
from datetime import datetime
from variable import *
import xmltodict
import time
import re
import cv2


class Device(object):
    """
    ip:设备ip
    port:设备HTTP端口号
    username：设备登录账号
    password:设备密码
    count:格式化次数
    nas_address:nas盘地址，选填
    nas_file_path:nas盘文件路径，选填
    nas_usernmae_CIFS账号，选填
    nas_password:CIFS密码，选填
    jianrong：SD卡兼容性测试，T/F
    """

    # 初始化
    def __init__(self, ip, port, username, password, count, nas_address=u'', nas_file_path=u'', nas_username=u'', nas_password=u'', jianrong=u'F'):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.nas_address = nas_address
        self.nas_file_path = nas_file_path
        self.nas_username = nas_username
        self.nas_password = nas_password
        self.count = int(count)
        self.result = []                  # 执行结果
        self.storage = 'sd' if nas_address == '' else 'nas'  #设备挂载的存储介质
        self.jianrong = jianrong          # 是否为测试SD卡兼容性

    # 登录设备
    def check(self):
        n = 0
        while True:
            try:
                n += 1
                put = requests.get(u'http://{0}:{1}{2}'.format(self.ip, self.port, check_status_url),
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                put.raise_for_status()
                print(u"设备登录成功")
                return True
            except Exception as e:
                if n >= 2:
                    return False

    # 添加nas盘
    def nas(self):
        n = 0
        while True:
            try:
                get_text = xmltodict.parse(nas_xml)
                get_text[u'nasList'][u'nas'][u'ipAddress'] = self.nas_address
                get_text[u'nasList'][u'nas'][u'path'] = self.nas_file_path
                if self.nas_username != '':
                    get_text[u'nasList'][u'nas'][u'userName'] = self.nas_username
                    get_text[u'nasList'][u'nas'][u'password'] = self.nas_password
                    get_text[u'nasList'][u'nas'][u'mountType'] = u'SMB/CIFS'

                put_text = xmltodict.unparse(get_text)
                put = requests.put(u'http://%s:%s' % (self.ip, self.port) + nas_url, data=put_text,
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=10)
                put.raise_for_status()
                print u"挂载NAS盘成功"
                print u"查看NAS盘状态"
                while True:
                    n += 1
                    print u"等待20秒"
                    time.sleep(15)
                    get = requests.get(u'http://%s:%s' % (self.ip, self.port) + storage_url,
                                       auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                    get_text1 = xmltodict.parse(get.text)
                    check = get_text1[u'storage'][u'nasList'][u'nas'][u'status']
                    if check == u'ok' or check == u'error' or check == u'unformatted':
                        print u'nas盘状态正常，可进行格式化'
                        return True
                    elif check == u'initializing':
                        print u"nas盘正在初始化中"
                        continue
                    if n >= 15:
                        print u"挂载nas盘失败"
                        self.result.append(u"测试结果：Failed\r\n挂载nas盘失败")
                        return False
            except Exception as e:
                print e
                print u"挂载nas盘失败"
                self.result.append(u"测试结果：Failed\r\n挂载nas盘失败")
                return False

    # 格式化NAS盘
    def format_nas(self):
        n = 0
        format_result = []
        format_time_result = []
        while n<self.count:
            try:
                n += 1
                print u'nas盘正在格式化'
                st = time.time()
                put = requests.put(u'http://%s:%s' % (self.ip, self.port) + nas_format_url,
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=10000)
                put.raise_for_status()
                et = time.time()
                format_time = round(et -st, 2)
                format_result.append(format_time)
                time.sleep(3)
                get2 = requests.get(u'http://%s:%s' % (self.ip, self.port) + storage_url,
                                    auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                get2.raise_for_status()
                get_text2 = xmltodict.parse(get2.text)
                check = get_text2[u'storage'][u'nasList'][u'nas'][u'status']
                if check == u'ok':
                    print u'第{0}次格式化成功，状态正常'.format(n)
                    format_information = u'第{0}次格式化耗时{1}s'.format(n, format_time)
                    format_time_result.append(format_information)
                    print format_information
                else:
                    print u'nas盘格式化成功，但状态异常'
                    self.result.append(u'测试结果：Failed\r\n提示：第{0}次nas格式化成功，但状态异常'.format(n))
                    print u'耗时{0}s'.format(format_time)
                    return False
            except Exception as e:
                print e
                print u"nas盘格式化失败"
                self.result.append(u'测试结果：Failed\r\n提示：nas盘格式化失败')
                return False
        average_time = round(sum(format_result)/len(format_result),2)
        result = u'\r\n'.join(format_time_result) + u"\r\n平均耗时为{0}s".format(average_time)
        self.result.append(u'测试结果：Pass\r\n'+result)
        return True

    # 检测SD卡挂载状态
    def hdd(self):
        try:
            get = requests.get('http://%s:%s' % (self.ip, self.port) + storage_url,
                               auth=HTTPDigestAuth(self.username, self.password), timeout=5)
            get_text = get.text.encode('utf-8')
            if '<id>1</id>' not in get_text:
                print(u'未识别到SD卡')
                self.result.append(u"测试结果：Failed\r\n原因：未识别到SD卡\r\n")
                return False
            else:
                get = requests.get(u'http://%s:%s' % (self.ip, self.port) + hdd_url,
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                get_text1 = xmltodict.parse(get.text)
                check = get_text1[u'hdd'][u'status']
                if check == u'ok' or check == u'error' or check == u'unformatted':
                    print u'SD卡状态正常，可进行格式化'
                    self.result.append(u"测试结果：Pass\r\n")
                    return True
                else:
                    print u"SD卡状态异常，无法格式化，请手动检查"
                    self.result.append(u"测试结果：Failed\r\n原因：SD卡状态异常，无法格式化，请手动检查\r\n")
                    return False
        except Exception as e:
            print u"检测SD卡失败，请手动检查"
            self.result.append(u"测试结果：Failed\r\n原因：检测SD卡失败，请手动检查\r\n")
            return False

    # 格式化SD卡
    def format_hdd(self):
        n = 0
        format_result = []
        format_time_result = []
        while n<self.count:
            try:
                n += 1
                print u'SD卡正在格式化'
                st = time.time()
                put = requests.put(u'http://%s:%s' % (self.ip, self.port) + format_url,
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=10000)
                put.raise_for_status()
                et = time.time()
                format_time = round(et -st, 2)
                format_result.append(format_time)
                time.sleep(3)
                get2 = requests.get(u'http://%s:%s' % (self.ip, self.port) + hdd_url,
                                    auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                get2.raise_for_status()
                get_text2 = xmltodict.parse(get2.text)
                check = get_text2[u'hdd'][u'status']
                if check == u'ok':
                    print u'第{0}次格式化成功，状态正常'.format(n)
                    format_information = u'第{0}次格式化耗时{1}s'.format(n, format_time)
                    format_time_result.append(format_information)
                    print format_information
                else:
                    print u'SD卡格式化成功，但状态异常'
                    self.result.append(u'测试结果：Failed\r\n提示：第{0}次SD卡格式化成功，但状态异常'.format(n))
                    print u'耗时{0}s'.format(format_time)
                    return False
            except Exception as e:
                print e
                print u"SD卡格式化失败"
                self.result.append(u'测试结果：Failed\r\n提示：SD卡格式化失败')
                return False
        average_time = round(sum(format_result)/len(format_result),2)
        result = u'\r\n'.join(format_time_result) + u"\r\n平均耗时为{0}s".format(average_time)
        self.result.append(u'测试结果：Pass\r\n'+result)
        return True

    # SD卡兼容性：首次检测SD卡挂载状态
    def hdd_1(self):
        try:
            get = requests.get('http://%s:%s' % (self.ip, self.port) + storage_url,
                               auth=HTTPDigestAuth(self.username, self.password), timeout=5)
            get_text = get.text.encode('utf-8')
            if '<id>1</id>' not in get_text:
                print(u'未识别到SD卡')
                self.result.append(u"1-1挂载，测试结果：Failed\r\n原因：未识别到SD卡\r\n")
                return False
            else:
                get = requests.get(u'http://%s:%s' % (self.ip, self.port) + hdd_url,
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                get_text1 = xmltodict.parse(get.text)
                check = get_text1[u'hdd'][u'status']
                if check == u'ok' or check == u'error' or check == u'unformatted':
                    print u'SD卡状态正常，可进行格式化'
                    self.result.append(u"1-1挂载，测试结果：Pass\r\n")
                    return True
                elif check == u'initializing':
                    print u'SD卡正在初始化，等待3秒后请再次点击执行'
                    self.result.append(u"1-1挂载，测试结果：Wait\r\n原因：SD卡正在初始化，等待3秒后请再次点击执行\r\n")
                    return False
                else:
                    print u"SD卡状态异常，无法格式化，请手动检查"
                    self.result.append(u"1-1挂载，测试结果：Failed\r\n原因：SD卡状态异常，无法格式化，请手动检查\r\n")
                    return False
        except Exception as e:
            print u"检测SD卡失败，请手动检查"
            self.result.append(u"1-1挂载，测试结果：Failed\r\n原因：检测SD卡失败，请手动检查\r\n")
            return False

    # SD卡兼容性：格式化SD卡
    def format_hdd_1(self):
        if self.record('false'):
            n = 0
            format_result = []
            format_time_result = []
            while n<self.count:
                try:
                    n += 1
                    print u'SD卡准备格式化'
                    st = time.time()
                    put = requests.put(u'http://%s:%s' % (self.ip, self.port) + format_url,
                                       auth=HTTPDigestAuth(self.username, self.password), timeout=10000)
                    put.raise_for_status()
                    et = time.time()
                    format_time = round(et -st, 2)
                    format_result.append(format_time)
                    time.sleep(3)
                    get2 = requests.get(u'http://%s:%s' % (self.ip, self.port) + hdd_url,
                                        auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                    get2.raise_for_status()
                    get_text2 = xmltodict.parse(get2.text)
                    check = get_text2[u'hdd'][u'status']
                    if check == u'ok':
                        print u'格式化成功，状态正常'
                        format_information = u'格式化耗时{0}s'.format(format_time)
                        format_time_result.append(format_information)
                        print format_information
                    else:
                        print u'SD卡格式化成功，但状态异常'
                        self.result.append(u"1-3格式化，测试结果：Failed\r\n原因：SD卡格式化成功，但状态异常\r\n")
                        print u'耗时{0}s'.format(format_time)
                        return False
                except Exception as e:
                    print e
                    print u"SD卡格式化失败"
                    self.result.append(u"1-3格式化，测试结果：Failed\r\n原因：SD卡格式化失败\r\n".format(n))
                    return False
            result = u'\r\n'.join(format_time_result)
            self.result.append(u'1-3格式化，测试结果：Pass\r\n'+result+u'\r\n')
            return True
        else:
            self.result.append(u"1-3格式化，测试结果：Failed\r\n原因：录像计划提前格式化前关闭失败\r\n")
            return False

    # 更改录像计划状态
    def record(self, status):
        n = 0
        while True:
            try:
                n += 1
                get = requests.get('http://%s:%s' % (self.ip, self.port) + record_url,
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                get_text = xmltodict.parse(get.text)
                get_text['TrackList']['Track'][0]['CustomExtensionList']['CustomExtension']['enableSchedule'] = status
                put_text = xmltodict.unparse(get_text)
                put = requests.put('http://%s:%s' % (self.ip, self.port) + record_url, data=put_text,
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                put.raise_for_status()
                if status == 'true':
                    print(u"开启通道1录像计划成功")
                else:
                    print(u"关闭通道1录像计划成功")
                return True
            except Exception as e:
                if n >= 3:
                    print(e)
                    if status == 'true':
                        print(u"开启通道1录像计划失败")
                    else:
                        print(u"关闭通道1录像计划失败")
                    return False

    # 配置7*24小时全天定时录像计划
    def record_plan(self):
        n = 0
        while True:
            try:
                n += 1
                get = requests.get('http://%s:%s' % (self.ip, self.port) + record_url,
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                get_text = get.text
                a = re.search("<TrackSchedule>", get_text).span()
                b = re.search("</TrackSchedule>", get_text).span()
                check = [a[1], b[0]]
                get_text = get_text.replace(get_text[check[0]:check[1]], allday_url)
                put = requests.put('http://%s:%s' % (self.ip, self.port) + record_url, data=get_text,
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                put.raise_for_status()
                print(u"全天录像计划配置成功")
                if self.record('true'):
                    print(u'开始录像10秒')
                    time.sleep(10)
                    print(u'已录好10秒的录像')
                    if self.record('false'):
                        return True
                    else:
                        return False
                else:
                    print(u'开启录像计划失败')
            except Exception as e:
                if n >= 3:
                    print(u"全天录像计划配置失败")
                    return False

    # SD卡兼容性：查询录像文件
    def search_recordfile(self):
        n = 0
        while True:
            n += 1
            root = xmltodict.parse(search_model_url)
            start_time = datetime.now().strftime("%Y-%m-%dT00:00:00Z")
            end_time = datetime.now().strftime("%Y-%m-%dT23:59:59Z")
            root['CMSearchDescription']['timeSpanList']['timeSpan']['startTime'] = start_time
            root['CMSearchDescription']['timeSpanList']['timeSpan']['endTime'] = end_time
            put_text = xmltodict.unparse(root)
            put = requests.post(u'http://{0}:{1}{2}'.format(self.ip, self.port, search_url),data=put_text,
                               auth=HTTPDigestAuth(self.username, self.password))
            get_text = xmltodict.parse(put.text)
            if get_text['CMSearchResult']['responseStatusStrg'] == u'OK':
                self.playbackURI = get_text['CMSearchResult']['matchList']['searchMatchItem']['mediaSegmentDescriptor'][
                    'playbackURI'][7:]
                print(u"成功查询到录像文件")
                return True
            else:
                time.sleep(5)
                print(u'等待5s')
                if n == 7:
                    print(u"查询录像文件失败")
                    return False
                else:
                    continue


    # SD卡兼容性：检查录像文件
    def check_recordfile(self):
        if self.record_plan():
            if self.search_recordfile():
                # 获取分辨率
                try:
                    capabilities = requests.get(u'http://{0}:{1}{2}'.format(self.ip, self.port, video_audio_url),
                                                auth=HTTPDigestAuth(self.username, self.password))
                    capabilities.raise_for_status()
                    capabilities_text = xmltodict.parse(capabilities.text)
                    videoResolutionHeight = int(
                        capabilities_text[u'StreamingChannelList'][u'StreamingChannel'][0][u'Video'][
                            u'videoResolutionHeight'])
                    videoResolutionWidth = int(
                        capabilities_text[u'StreamingChannelList'][u'StreamingChannel'][0][u'Video'][
                            u'videoResolutionWidth'])
                    video = (videoResolutionHeight, videoResolutionWidth)
                    cap = cv2.VideoCapture(u'rtsp://{0}:{1}@{2}'.format(self.username, self.password, self.playbackURI))
                    ret, frame = cap.read()
                    if video == frame.shape[0:2]:
                        a = 0
                        while ret:
                            a += 1
                            ret, frame = cap.read()
                            cv2.imshow("frame", frame)
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break
                            if a > 100:
                                print(u'录像读写成功')
                                break
                        cv2.destroyAllWindows()
                        cap.release()
                        self.result.append(u"1-4读写录像，测试结果：Pass\r\n")
                        return True
                    else:
                        print(u"录像的分辨率与设备不匹配")
                        self.result.append(u"1-4读写录像，测试结果：Failed\r\n原因：录像的分辨率与设备不匹配\r\n")
                        return False
                except Exception as e:
                    print(e)
                    print(u"检查录像失败")
                    self.result.append(u"1-4读写录像，测试结果：Failed\r\n原因：检查录像失败\r\n")
                    return False
            else:
                self.result.append(u"1-4读写录像，测试结果：Failed\r\n原因：查询录像文件失败\r\n")
                return False
        else:
            self.result.append(u"1-4读写录像，测试结果：Failed\r\n原因：录像计划配置失败\r\n")
            return False


    # 设备校时
    def check_time(self):
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
                self.result.append(u"1-2登录&校时，测试结果：Pass\r\n")
                return True
            except Exception as e:
                if n >= 3:
                    print(u"校时失败")
                    self.result.append(u"1-2登录&校时，测试结果：Failed\r\n原因：校时失败\r\n")
                    return False

    # SD卡兼容性：检查设备日志
    def check_log(self):
        try:
            root = xmltodict.parse(log_model_url)
            start_time = datetime.now().strftime("%Y-%m-%dT00:00:00Z")
            end_time = datetime.now().strftime("%Y-%m-%dT23:59:59Z")
            root['CMSearchDescription']['timeSpanList']['timeSpan']['startTime'] = start_time
            root['CMSearchDescription']['timeSpanList']['timeSpan']['endTime'] = end_time
            put_text = xmltodict.unparse(root)
            put = requests.post(u'http://{0}:{1}{2}'.format(self.ip, self.port, log_url),data=put_text,
                               auth=HTTPDigestAuth(self.username, self.password))
            get_text = xmltodict.parse(put.text)
            if get_text['CMSearchResult']['responseStatus'] == u'true':
                self.log_nums = get_text['CMSearchResult']['numOfMatches']
                print(u"成功查询到日志文件")
                self.result.append(u"1-5读写日志，测试结果：Pass\r\n")
                return True
            else:
                print(u"未查询到日志文件")
                self.result.append(u"1-5读写日志，测试结果：Failed\r\n原因：未查询到日志文件\r\n")
                return False
        except Exception as e:
            print(u"查询日志文件失败")
            self.result.append(u"1-5读写日志，测试结果：Failed\r\n原因：查询日志文件失败\r\n")
            return False

    # SD卡兼容性：检查设备是否上线
    def check_status(self):
        n = 0
        while True:
            try:
                n += 1
                put = requests.get('http://{0}:{1}{2}'.format(self.ip, self.port, check_status_url),
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=10)
                put.raise_for_status()
                print(u"设备上线成功！！")
                return True
            except Exception as e:
                # 若超过10分钟未检测到设备在线，报错
                if n >= 100:
                    return False

    # SD卡兼容性：重启
    def reboot(self):
        # 重启执行
        try:
            print(u"设备开始重启")
            put = requests.put('http://{0}:{1}{2}'.format(self.ip, self.port, reboot_url),
                               auth=HTTPDigestAuth(self.username, self.password), timeout=10)
            put.raise_for_status()
            st = time.time()
            time.sleep(30)
            if self.check_status():
                et = time.time()
                reboot_time = round(et - st, 2)
                print(u"设备重启成功，耗时{0}s".format(reboot_time))
                self.result.append(u"1-6重启，测试结果：Pass\r\n重启耗时{0}s\r\n".format(reboot_time))
                return True
            else:
                print(u"设备长达8分钟未起来，请检查！！")
                self.result.append(u"1-6重启，测试结果：Failed\r\n原因：设备长达5分钟未起来\r\n")
                return False
        except Exception as e:
            print(u"执行重启操作失败！")
            self.result.append(u"1-6重启，测试结果：Failed\r\n原因：执行重启操作失败\r\n")
            return False

    # SD卡兼容性：重启后检查SD卡挂载状态
    def hdd_2(self):
        n = 0
        while True:
            try:
                n += 1
                get = requests.get('http://%s:%s' % (self.ip, self.port) + storage_url,
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                get_text = get.text.encode('utf-8')
                if '<id>1</id>' in get_text:
                    print(u'识别到SD卡')
                    self.result.append(u"1-7挂载1，测试结果：Pass\r\n")
                    return True
            except Exception as e:
                if n >= 4:
                    print u"未识别到SD卡，请手动检查"
                    self.result.append(u"1-7挂载1，测试结果：Failed\r\n原因：未识别到SD卡，请手动检查\r\n")
                    return False

    # SD卡兼容性：重启后检查SD卡挂载状态
    def hdd_3(self):
        n = 0
        while True:
            try:
                n += 1
                get = requests.get(u'http://%s:%s' % (self.ip, self.port) + hdd_url,
                                   auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                get_text1 = xmltodict.parse(get.text)
                check = get_text1[u'hdd'][u'status']
                if check == u'ok':
                    print u'SD卡状态正常'
                    self.result.append(u"1-7挂载2，测试结果：Pass\r\n")
                    return True
            except Exception as e:
                if n >= 4:
                    print u"SD卡状态异常"
                    self.result.append(u"1-7挂载2，测试结果：Failed\r\n原因：SD卡状态异常，请手动检查\r\n")
                    return False

    # SD卡兼容性：重启后检查设备日志
    def check_log_again(self):
        try:
            root = xmltodict.parse(log_model_url)
            start_time = datetime.now().strftime("%Y-%m-%dT00:00:00Z")
            end_time = datetime.now().strftime("%Y-%m-%dT23:59:59Z")
            root['CMSearchDescription']['timeSpanList']['timeSpan']['startTime'] = start_time
            root['CMSearchDescription']['timeSpanList']['timeSpan']['endTime'] = end_time
            put_text = xmltodict.unparse(root)
            put = requests.post(u'http://{0}:{1}{2}'.format(self.ip, self.port, log_url),data=put_text,
                               auth=HTTPDigestAuth(self.username, self.password))
            get_text = xmltodict.parse(put.text)
            if get_text['CMSearchResult']['responseStatus'] == u'true':
                if get_text['CMSearchResult']['numOfMatches'] > self.log_nums:
                    print(u"成功查询到日志文件被修改")
                    self.result.append(u"1-8重启读写日志，测试结果：Pass\r\n")
                    return True
                else:
                    print(u"未查询到日志文件被修改")
                    self.result.append(u"1-8重启读写日志，测试结果：Failed\r\n原因：未查询到日志文件被修改\r\n")
                    return False
            else:
                print(u"未查询到日志文件")
                self.result.append(u"1-8重启读写日志，测试结果：Failed\r\n原因：未查询到日志文件\r\n")
                return False
        except Exception as e:
            print(u"查询日志文件失败")
            self.result.append(u"1-8重启读写日志，测试结果：Failed\r\n原因：查询日志文件失败\r\n")
            return False

    # 总流程
    def test(self):
        # 判定工具运行模式
        if self.jianrong == 'F':
            if self.storage == 'nas':
                if self.nas():
                    self.format_nas()
            else:
                if self.hdd():
                    self.format_hdd()
        else:
            if self.hdd_1():
                if self.check_time():
                    if self.format_hdd_1():
                        if self.check_recordfile():
                            if self.check_log():
                                if self.check_time():
                                    if self.reboot():
                                        if self.hdd_2():
                                            if self.hdd_3():
                                                self.check_log_again()

    # SD卡兼容性：重启后检查SD卡挂载状态
    def emmc(self):
        try:
            get = requests.get('http://%s:%s' % (self.ip, self.port) + storage_url,
                               auth=HTTPDigestAuth(self.username, self.password), timeout=6)
            get_text = get.text.encode('utf-8')
            if '<id>2</id>' not in get_text:
                print(u'未识别到EMMC')
                self.result.append(u"EMMC格式化，测试结果：Failed\r\n原因：未识别到EMMC\r\n")
                return False
            else:
                if '<id>1</id>' not in get_text:
                    get = requests.get(u'http://%s:%s' % (self.ip, self.port) + hdd_url,
                                       auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                    get_text1 = xmltodict.parse(get.text)
                    check = get_text1[u'hdd'][u'status']
                    if check == u'ok' or check == u'error' or check == u'unformatted':
                        print u'EMMC状态正常'
                        return True
                    else:
                        print u"EMMC状态异常，请手动检查"
                        self.result.append(u"EMMC格式化，测试结果：Failed\r\n原因：EMMC状态异常\r\n")
                        return False
                else:
                    get = requests.get(u'http://%s:%s' % (self.ip, self.port) + emmc_url,
                                       auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                    get_text1 = xmltodict.parse(get.text)
                    check = get_text1[u'hdd'][u'status']
                    if check == u'ok' or check == u'error' or check == u'unformatted':
                        print u'EMMC状态正常'
                        return True
                    else:
                        print u"EMMC状态异常，请手动检查"
                        self.result.append(u"EMMC格式化，测试结果：Failed\r\n原因：EMMC状态异常\r\n")
                        return False
        except Exception as e:
            print u"检测EMMC失败，请手动检查"
            self.result.append(u"EMMC格式化，测试结果：Failed\r\n原因：检测EMMC状态失败\r\n")
            return False

    # SD卡兼容性：格式化SD卡
    def format_emmc(self):
        if self.record('false'):
            n = 0
            while n<self.count:
                try:
                    n += 1
                    get = requests.get('http://%s:%s' % (self.ip, self.port) + storage_url,
                                       auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                    get_text = get.text.encode('utf-8')
                    if '<id>1</id>' in get_text:
                        print u'EMMC正在格式化'
                        put = requests.put(u'http://%s:%s' % (self.ip, self.port) + format_emmc_url,
                                           auth=HTTPDigestAuth(self.username, self.password), timeout=10000)
                        put.raise_for_status()
                        time.sleep(3)
                        get2 = requests.get(u'http://%s:%s' % (self.ip, self.port) + emmc_url,
                                            auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                        get2.raise_for_status()
                        get_text2 = xmltodict.parse(get2.text)
                        check = get_text2[u'hdd'][u'status']
                        if check == u'ok':
                            print u'EMMC格式化成功，状态正常'
                        else:
                            print u'EMMC格式化成功，但状态异常'
                            self.result.append(u"EMMC格式化，测试结果：Failed\r\n原因：EMMC格式化成功格式化成功，但状态异常\r\n")
                            return False
                    else:
                        print u'EMMC正在格式化'
                        put = requests.put(u'http://%s:%s' % (self.ip, self.port) + format_emmc_url,
                                           auth=HTTPDigestAuth(self.username, self.password), timeout=10000)
                        put.raise_for_status()
                        time.sleep(3)
                        get2 = requests.get(u'http://%s:%s' % (self.ip, self.port) + hdd_url,
                                            auth=HTTPDigestAuth(self.username, self.password), timeout=5)
                        get2.raise_for_status()
                        get_text2 = xmltodict.parse(get2.text)
                        check = get_text2[u'hdd'][u'status']
                        if check == u'ok':
                            print u'EMMC格式化成功，状态正常'
                        else:
                            print u'EMMC格式化成功，但状态异常'
                            self.result.append(u"EMMC格式化，测试结果：Failed\r\n原因：EMMC格式化成功格式化成功，但状态异常\r\n")
                            return False
                except Exception as e:
                    print e
                    print u"EMMC格式化成功格式化失败"
                    self.result.append(u"EMMC格式化，测试结果：Failed\r\n原因：EMMC格式化失败\r\n".format(n))
                    return False
            self.result.append(u'EMMC格式化，测试结果：Pass\r\n')
            return True
        else:
            self.result.append(u"EMMC格式化，测试结果：Failed\r\n原因：录像计划在格式化前关闭失败\r\n")
            return False

    # EMMC测试前检查
    def EMMC_check(self):
        if self.emmc():
            self.format_emmc()

if __name__ == '__main__':
    A = Device('10.65.150.192', '80', 'admin', 'abcd1234', '1', jianrong=u'T')
    A.record_plan()