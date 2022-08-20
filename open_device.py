# -*- coding: utf-8 -*-
import openpyxl
import threading
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from public_function import getColValues


class MyThread(threading.Thread):
    """
    ip:设备ip
    username：设备登录账号
    password:设备密码
    """

    # 初始化
    def __init__(self, ip, username, password):
        threading.Thread.__init__(self)
        self.ip   = ip
        self.user = username
        self.pwd  = password

    # 业务逻辑
    def run(self):
        try:
            # 使用IE
            driver = webdriver.Ie()
            # 全屏
            driver.maximize_window()
            # 打开设备登录界面
            driver.get('http://' + self.ip)
            # 设置动作
            action = ActionChains(driver)
            # 输入账号密码并回车，超时30秒
            WebDriverWait(driver, 30).until(
                lambda driver: driver.find_element_by_xpath('//div[@class="login-user"]/input[@type="text"]'))
            action.send_keys_to_element(driver.find_element_by_xpath('//div[@class="login-user"]/input[@type="text"]'),
                                        self.user).send_keys(Keys.TAB).send_keys(self.pwd, Keys.ENTER).perform()

            # 点击配置按钮，超时30秒
            WebDriverWait(driver, 30).until(lambda driver: driver.find_element_by_xpath('//ul[@id="nav"]/li/a[@ng-bind="oLan.config"]'))
            driver.find_element_by_xpath('//ul[@id="nav"]/li/a[@ng-bind="oLan.config"]').click()
            self.result = u'{0}：开启IE控件成功'.format(self.ip)
        except Exception as e:
            print(u"{0}执行失败".format(self.ip))
            self.result = u'{0}：开启IE控件失败'.format(self.ip)


def open_device():
    # 关闭IE安全模式
    DesiredCapabilities.INTERNETEXPLORER['ignoreProtectedModeSettings'] = True

    # 打开Excel配置文件，获取设备信息
    data = openpyxl.load_workbook('devices/devices.xlsx')
    table = data[u'批量开IE']
    devices = list(filter(None, getColValues(table, 1)))[1:]
    username = list(filter(None, getColValues(table, 2)))[1:]
    password = list(filter(None, getColValues(table, 3)))[1:]

    # 业务执行
    print(u'开始执行!!')
    li = []
    nums = len(devices)
    for i in range(nums):
        t = MyThread(devices[i], username[i], password[i])
        li.append(t)
        t.start()
    for t in li:
        t.join()
    print(u'执行完毕!!')

    # 结果回填
    result = []
    for i in li:
        result.append(i.result)
    return result


if __name__ == '__main__':
    open_device()