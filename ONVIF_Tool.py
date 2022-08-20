# -*- coding: utf-8 -*-
from PyQt4.QtGui import QPushButton, QWidget, QLabel, QApplication, QLineEdit, QGridLayout, QTextBrowser, QMessageBox, \
    QFont, QRegExpValidator,QTextCursor,QTextEdit
from PyQt4 import QtCore
from PyQt4.QtCore import QRegExp
from ONVIF_Device import Device
from public_function import validate_ip
from log import Stream
import sys


# GUI界面函数
class GUI(QWidget):
    # GUI初始化
    def __init__(self, parent=None):
        super(GUI, self).__init__(parent)

        # 初始化界面
        self.setup_ui()

        # 实例化计时器子线程对象
        self.my_thread = MyThread()
        self.my_thread.my_signal.connect(self.set_label_func)

        # 按钮响应
        self.button.clicked.connect(self.work)

        # 将打印输出到日志打印控件
        sys.stdout = Stream(newText=self.onUpdateText)

    # 设置GUI界面
    def setup_ui(self):
        # 设置输入限制
        reg_math = QRegExp('[0-9]+$')
        validator_math = QRegExpValidator(self)
        validator_math.setRegExp(reg_math)

        # IP控件
        self.label_ip = QLabel(u'设备IP地址')
        self.line_ip = QLineEdit()

        # 用户名控件
        self.label_username = QLabel(u'用户名')
        self.line_username = QLineEdit('admin')

        # 密码控件
        self.label_password = QLabel(u'密码')
        self.line_password = QLineEdit('abcd1234')

        # 录像通道控件
        self.label_channel = QLabel(u'录像通道')
        self.line_channel = QLineEdit('1')
        self.line_channel.setValidator(validator_math)

        # NAS服务器地址控件
        self.label_nas_server_address = QLabel(u'NAS服务器地址')
        self.line_nas_server_address = QLineEdit()

        # NAS文件路径控件
        self.label_nas_file_path = QLabel(u'NAS文件路径')
        self.line_nas_file_path = QLineEdit()

        # 简单恢复控件
        self.label_restore = QLabel(u'是否简单恢复(T/F)')
        self.line_restore = QLineEdit('T')

        # 执行按钮控件
        self.button = QPushButton(u"点击运行")

        # 执行结果控件
        self.label_result = QLabel(u"执行结果")
        self.QTextBrowser = QTextBrowser()
        self.QTextBrowser.setStyleSheet("font-size:16px;font-weight:bold;font-family:Microsoft YaHei;")

        # 计时器控件
        self.label_time2 = QLabel(u"0")

        # 使用说明控件
        self.label_msg = QLabel(u"使用说明\r\n---------\r\n打印信息")
        self.process = QTextEdit(self, readOnly=True)
        self.process.setPlainText(     u"功能：自动配置设备ONVIF工具测试前所需的参数\r\n"
                                       u"1、必填项：IP地址、用户名、密码、录像通道\r\n"
                                       u"2、选填项：是否简单恢复,NAS相关信息\r\n"
                                       u"3、若没有填写NAS,则默认设备挂载SD卡\r\n"
                                       u"4、点击按钮后计时器计时,代表工具正在运行,切勿多次点击\r\n"
                                       u"5、执行过程打印在CMD框,执行完毕后结果反馈在执行结果框")


        # 水平盒式布局
        layout = QGridLayout()

        # 添加控件
        layout.addWidget(self.label_ip, 0, 0)
        layout.addWidget(self.line_ip, 0, 1)
        layout.addWidget(self.label_username, 0, 2)
        layout.addWidget(self.line_username, 0, 3)
        layout.addWidget(self.label_password, 0, 4)
        layout.addWidget(self.line_password, 0, 5)
        layout.addWidget(self.label_channel, 0, 6)
        layout.addWidget(self.line_channel, 0, 7)
        layout.addWidget(self.label_nas_server_address, 1, 0)
        layout.addWidget(self.line_nas_server_address, 1, 1)
        layout.addWidget(self.label_nas_file_path, 1, 2)
        layout.addWidget(self.line_nas_file_path, 1, 3)
        layout.addWidget(self.label_restore, 1, 4)
        layout.addWidget(self.line_restore, 1, 5)
        layout.addWidget(self.button, 1, 6)
        layout.addWidget(self.label_time2, 1, 7)
        layout.addWidget(self.label_msg, 2, 0)
        layout.addWidget(self.process, 2, 1, 2, 3)
        layout.addWidget(self.label_result, 2, 4)
        layout.addWidget(self.QTextBrowser, 2, 5, 2, 7)

        # 设置布局
        self.setLayout(layout)

        # 工具标题
        self.setWindowTitle(u"ONVIF参数配置工具")

        # 设置字体样式
        self.setFont(QFont("Microsoft YaHei", 10))

    # 更新打印信息
    def onUpdateText(self, text):
        """Write console output to text widget."""
        cursor = self.process.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(unicode(text))
        self.process.setTextCursor(cursor)
        self.process.ensureCursorVisible()

    # 参数配置子线程执行函数
    def work(self):
        # 清空各个输出框的信息
        self.QTextBrowser.setPlainText("")
        self.process.setText("")
        self.label_time2.setText("0")

        # 将打印输出到日志打印控件
        sys.stdout = Stream(newText=self.onUpdateText)

        # IP地址数据校验
        if not validate_ip(self.line_ip.text()):
            QMessageBox.information(self, u"提示", u"设备IP地址错误", QMessageBox.Yes)
            return

        # 检测设备是否在线
        if not Device(self.line_ip.text(), self.line_username.text(),
                      self.line_password.text()).check():
            QMessageBox.information(self, u"提示", u"登录设备失败，请检查参数是否配置正确", QMessageBox.Yes)
            return

        # 获取用户输入的数据
        self.data = [self.line_ip.text(), self.line_username.text(),
                     self.line_password.text(), self.line_nas_server_address.text(), self.line_nas_file_path.text(),
                     self.line_restore.text(),self.line_channel.text()]

        # 启动业务子线程和计时器子线程
        self.thread = RunThread(self.data)
        self.thread.trigger.connect(self.ride)
        self.thread.start()

        # 启动计时器子线程
        self.my_thread.is_on = True
        self.my_thread.start()

    # 参数配置子线程函数结束后进行数据回填
    def ride(self, result):
        try:
            # 回填执行结果
            self.QTextBrowser.append(u"简单恢复：" + result[0])
            self.QTextBrowser.append(u"关闭夏令时：" + result[1])
            self.QTextBrowser.append(u"校时：" + result[2])

            for i in range(len(result[3])):
                self.QTextBrowser.append(u"通道{}修改视频参数：{}".format(str(i+1), result[3][i]))

            self.QTextBrowser.append(u"开启IPV6路由公告：" + result[4])
            self.QTextBrowser.append(u"关闭HTTPS：" + result[5])

            for j in range(len(result[6])):
                self.QTextBrowser.append(u"通道{}关闭WDR：{}".format(str(j+1), result[6][j]))

            self.QTextBrowser.append(u"开启ONVIF：" + result[7])
            self.QTextBrowser.append(u"创建ONVIF用户：" + result[8])
            self.QTextBrowser.append(u"格式化存储：" + result[9])
            self.QTextBrowser.append(u"录像2分钟：" + result[10])

            # 停止计时器
            self.my_thread.is_on = False
            QMessageBox.information(self, u"提示", u"执行完毕，请查看结果", QMessageBox.Yes)
        except Exception as e:
            # 停止计时器
            self.my_thread.is_on = False
            QMessageBox.information(self, u"提示", u"执行出错，请检查填写的参数与设备本身", QMessageBox.Yes)

    # 计时器更新
    def set_label_func(self, num):
        self.label_time2.setText(num)


# 业务执行-子线程
class RunThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(list)

    # 初始化数据
    def __init__(self, data):
        super(RunThread, self).__init__()
        self.data = data

    # 处理业务逻辑
    def run(self):
        device = Device(self.data[0], self.data[1], self.data[2],
                        self.data[3], self.data[4], self.data[5],
                        self.data[6])
        device.test()
        self.trigger.emit(device.result)


# 计时器-子线程
class MyThread(QtCore.QThread):  # 线程类
    my_signal = QtCore.pyqtSignal(str)  # 自定义信号对象。参数str就代表这个信号可以传一个字符串

    def __init__(self):
        super(MyThread, self).__init__()
        self.count = 0
        self.is_on = True

    # 运行计时器
    def run(self):
        while self.is_on:
            self.count += 1
            self.my_signal.emit(str(self.count))  # 释放自定义的信号
            self.sleep(1)  # 本线程睡眠1秒，即计时作用

