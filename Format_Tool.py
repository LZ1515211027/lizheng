# -*- coding: utf-8 -*-
from PyQt4.QtGui import QPushButton, QWidget, QLabel, QApplication, QLineEdit, QGridLayout, QTextBrowser, QMessageBox, \
    QFont, QRegExpValidator,QTextCursor,QTextEdit
from PyQt4 import QtCore
from PyQt4.QtCore import QRegExp
from Format_Device import *
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

        # 实例化业务子线程对象
        self.thread = RunThread()
        self.thread.trigger.connect(self.ride)
        self.thread_EMMC = RunThread_EMMC()
        self.thread_EMMC.trigger.connect(self.ride_EMMC)

        # 按钮响应
        self.button.clicked.connect(self.work)
        self.button_EMMC.clicked.connect(self.EMMC)

    # 设置GUI界面
    def setup_ui(self):
        # IP地址输入限制
        reg_math = QRegExp(u'[0-9]+$')
        validator_math = QRegExpValidator(self)
        validator_math.setRegExp(reg_math)

        # IP控件
        self.label_ip = QLabel(u'设备IP地址')
        self.line_ip = QLineEdit()

        # 用户名控件
        self.label_username = QLabel(u'用户名')
        self.line_username = QLineEdit(u'admin')

        # 密码控件
        self.label_password = QLabel(u'密码')
        self.line_password = QLineEdit(u'abcd1234')

        # NAS服务器地址控件
        self.label_nas_server_address = QLabel(u'NAS服务器地址')
        self.line_nas_server_address = QLineEdit()

        # NAS文件路径控件
        self.label_nas_file_path = QLabel(u'NAS文件路径')
        self.line_nas_file_path = QLineEdit()

        # 格式化次数
        self.label_count = QLabel(u'格式化次数')
        self.line_count = QLineEdit(u'1')

        # NAS账号控件
        self.label_nas_username = QLabel(u'NAS账号')
        self.line_nas_username = QLineEdit()

        # NAS密码控件
        self.label_nas_password = QLabel(u'NAS密码')
        self.line_nas_password = QLineEdit()

        # NAS密码控件
        self.label_jianrong = QLabel(u'SD卡兼容性?(T/F)')
        self.line_jianrong = QLineEdit(u'T')


        # 执行按钮控件
        self.button_EMMC = QPushButton(u"格式化EMMC")
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
        self.process.setPlainText(
                                  u"SD卡兼容性测试：\r\n"
                                  u"1、SD卡兼容性需填写T，格式化次数填写1，NAS信息无需填写\r\n"
                                  u"2、EMMC设备首次使用，需点击一次格式化EMMC！！\r\n"
                                  u"3、换卡后，点击运行按钮即可，会自动检测SD卡挂载情况\r\n"
                                  u"4、全自动化执行，请勿打开设备控件，可能影响工具执行\r\n"
                                  u"注意！！坏卡请单独手动测试，需验证插卡后设备运行无异常\r\n"
                                  u"\r\n普通格式化：\r\n"
                                  u"1、根据填写的格式化次数对挂载的SD卡或NAS进行格式化\r\n"
                                  u"2、输出每次格式化的耗时和平均耗时\r\n"
                                  u"3、填写设备IP地址、用户名、密码，格式化次数，SD卡兼容性为F\r\n"
                                  u"4、测试SD卡，则NAS信息无需填写；挂载CIFS需要填写账号密码\r\n"
                                  u"5、进行下一个NAS盘格式化时，只需重新填写nas盘信息即可"
        )

        # 水平盒式布局
        layout = QGridLayout()

        # 添加控件
        layout.addWidget(self.label_ip, 0, 0)
        layout.addWidget(self.line_ip, 0, 1)
        layout.addWidget(self.label_username, 0, 2)
        layout.addWidget(self.line_username, 0, 3)
        layout.addWidget(self.label_password, 0, 4)
        layout.addWidget(self.line_password, 0, 5)
        layout.addWidget(self.label_count, 0, 6)
        layout.addWidget(self.line_count, 0, 7)
        layout.addWidget(self.label_jianrong, 2, 0)
        layout.addWidget(self.line_jianrong, 2, 1)
        layout.addWidget(self.button, 2, 7)
        layout.addWidget(self.label_time2, 2, 6)
        layout.addWidget(self.button_EMMC, 2, 3)
        layout.addWidget(self.label_nas_server_address, 1, 0)
        layout.addWidget(self.line_nas_server_address, 1, 1)
        layout.addWidget(self.label_nas_file_path, 1, 2)
        layout.addWidget(self.line_nas_file_path, 1, 3)
        layout.addWidget(self.label_nas_username, 1, 4)
        layout.addWidget(self.line_nas_username, 1, 5)
        layout.addWidget(self.label_nas_password, 1, 6)
        layout.addWidget(self.line_nas_password, 1, 7)
        layout.addWidget(self.label_msg, 3, 0)
        layout.addWidget(self.process, 3, 1, 3, 3)
        layout.addWidget(self.label_result, 3, 4)
        layout.addWidget(self.QTextBrowser, 3, 5, 3, 7)

        # 设置布局
        self.setLayout(layout)

        # 工具标题
        self.setWindowTitle(u"格式化nas盘工具")

        # 设置字体样式
        self.setFont(QFont(u"Microsoft YaHei", 10))

    # 更新打印信息
    def onUpdateText(self, text):
        """Write console output to text widget."""
        cursor = self.process.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(unicode(text))
        self.process.setTextCursor(cursor)
        self.process.ensureCursorVisible()

    # 执行按钮点击后的逻辑
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

        # 设备在线检测
        if not Device(self.line_ip.text(), u'80', self.line_username.text(),
                     self.line_password.text(), self.line_count.text(), self.line_nas_server_address.text(), self.line_nas_file_path.text(),
                     self.line_nas_username.text(), self.line_nas_password.text()).check():
            QMessageBox.information(self, u"提示", u"登录设备失败，请检查参数是否配置正确", QMessageBox.Yes)
            return

        # 启动业务子线程和计时器子线程
        self.data = [self.line_ip.text(), u'80', self.line_username.text(),self.line_password.text(),
                     self.line_count.text(), self.line_nas_server_address.text(), self.line_nas_file_path.text(),
                     self.line_nas_username.text(), self.line_nas_password.text(), self.line_jianrong.text()]
        self.thread.set_parm(self.data)
        self.thread.start()
        self.my_thread.is_on = True
        self.my_thread.start()

    def EMMC(self):
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

        # 设备在线检测
        if not Device(self.line_ip.text(), u'80', self.line_username.text(),
                     self.line_password.text(), self.line_count.text(), self.line_nas_server_address.text(), self.line_nas_file_path.text(),
                     self.line_nas_username.text(), self.line_nas_password.text()).check():
            QMessageBox.information(self, u"提示", u"登录设备失败，请检查参数是否配置正确", QMessageBox.Yes)
            return

        # 启动业务子线程和计时器子线程
        self.data = [self.line_ip.text(), u'80', self.line_username.text(),self.line_password.text(),
                     self.line_count.text(), self.line_nas_server_address.text(), self.line_nas_file_path.text(),
                     self.line_nas_username.text(), self.line_nas_password.text(), self.line_jianrong.text()]
        self.thread_EMMC.set_parm(self.data)
        self.thread_EMMC.start()
        self.my_thread.is_on = True
        self.my_thread.start()

    # 执行子线程函数结束后进行数据回填
    def ride(self, result):
        try:
            # 回填执行结果
            for i in result:
                self.QTextBrowser.insertPlainText(i)

            # 停止计时器
            self.my_thread.is_on = False
            QMessageBox.information(self, u"提示", u"执行完毕，请查看结果", QMessageBox.Yes)
        except Exception as e:
            self.my_thread.is_on = False
            QMessageBox.information(self, u"提示", u"执行出错，请检查填写的参数与设备本身", QMessageBox.Yes)

    def ride_EMMC(self, result):
        try:
            # 回填执行结果
            for i in result:
                self.QTextBrowser.insertPlainText(i)

            # 停止计时器
            self.my_thread.is_on = False
            QMessageBox.information(self, u"提示", u"执行完毕，请查看结果", QMessageBox.Yes)
        except Exception as e:
            self.my_thread.is_on = False
            QMessageBox.information(self, u"提示", u"执行出错，请检查填写的参数与设备本身", QMessageBox.Yes)

    # 计时器更新
    def set_label_func(self, num):
        self.label_time2.setText(num)


# 业务执行-子线程
class RunThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(list)

    # 初始化数据
    def __init__(self):
        super(RunThread, self).__init__()


    def set_parm(self,data):
        self.device = Device(data[0], data[1], data[2],
                             data[3], data[4], data[5],
                             data[6], data[7],data[8],data[9])
    # 处理业务逻辑
    def run(self):
        self.device.test()
        self.trigger.emit(self.device.result)

class RunThread_EMMC(QtCore.QThread):
    trigger = QtCore.pyqtSignal(list)

    # 初始化数据
    def __init__(self):
        super(RunThread_EMMC, self).__init__()


    def set_parm(self,data):
        self.device = Device(data[0], data[1], data[2],
                             data[3], data[4], data[5],
                             data[6], data[7],data[8],data[9])
    # 处理业务逻辑
    def run(self):
        self.device.EMMC_check()
        self.trigger.emit(self.device.result)

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


if __name__ == '__main__':
    A = Device('10.65.73.153','80','admin','abcd1234','1',jianrong='T')
    A.check_time()