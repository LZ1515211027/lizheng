# -*- coding: utf-8 -*-
from PyQt4.QtGui import QPushButton, QWidget, QLabel, QApplication, QGridLayout, QTextBrowser, QMessageBox, QFont,QTextCursor,QTextEdit
from PyQt4 import QtCore
import open_device
import cfg_tool
import format_stability
import NVR_Tool
import bohao_check
import os
from public_function import sort_file_by_time
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
        self.my_thread = TimeThread()
        self.my_thread.my_signal.connect(self.set_label_func)

        # 按钮响应
        self.button_ie.clicked.connect(self.ie)
        self.button_cfg_out.clicked.connect(self.cfg_out)
        self.button_cfg_in.clicked.connect(self.cfg_in)
        self.button_format.clicked.connect(self.format)
        self.button_nvr.clicked.connect(self.nvr)
        self.button_excel.clicked.connect(self.excel)
        self.button_report.clicked.connect(self.report)
        self.button_bohao.clicked.connect(self.bohao)

    # 设置GUI界面
    def setup_ui(self):
        # 执行按钮控件
        self.label_1 = QLabel(u"功能1")
        self.label_2 = QLabel(u"功能2")
        self.label_3 = QLabel(u"功能3")
        self.label_4 = QLabel(u"功能4")
        self.label_5 = QLabel(u"功能5")
        self.label_6 = QLabel(u"功能6")
        self.button_cfg_out = QPushButton(u"批量参数导出")
        self.button_cfg_in = QPushButton(u"批量参数导入")
        self.button_ie = QPushButton(u"批量开IE控件")
        self.button_format = QPushButton(u"大面积格式化")
        self.button_nvr = QPushButton(u"批量导入NVR")
        self.button_bohao = QPushButton(u"拨号状态检查")
        self.button_excel = QPushButton(u"打开devices.xlsx进行配置")
        self.button_excel.setStyleSheet("font-size:15px;font-weight:bold;")
        self.button_report = QPushButton(u"打开大面积格式化报告")
        self.button_report.setStyleSheet("font-size:15px;font-weight:bold;")

        # 执行结果控件
        self.label_result = QLabel(u"执行结果")
        self.QTextBrowser = QTextBrowser()
        self.QTextBrowser.setStyleSheet("font-size:16px;font-weight:bold;font-family:Microsoft YaHei;")

        # 计时器控件
        self.label_time1 = QLabel(u"计时器")
        self.label_time2 = QLabel(u"0")

        # 使用说明控件
        self.label_msg = QLabel(u"使用说明\r\n---------\r\n打印信息")
        self.process = QTextEdit(self, readOnly=True)
        self.process.setPlainText(u"各项功能均需在文件夹devices下的devices.xlsx中配置设备信息,不同功能对应不同Sheet页,可点击按钮直接打开devices.xlsx\r\n"
                                  u"①大面积格式化：\r\n"
                                  u"1、进入对应的Sheet页,填写参数\r\n"
                                  u"2、点击按钮执行,设备将按照设定的次数进行格式化\r\n"
                                  u"3、执行过程反馈在CMD框中,具体结果会生成在文件夹devices下的report.xlsx中,可点击按钮直接打开报告\r\n"
                                  u"②批量参数导入导出：\r\n"
                                  u"1、进入对应的Sheet页,填写参数\r\n"
                                  u"2、点击导出按钮,设备的参数文件会导出至Config_file文件夹中,文件按照设备IP命名\r\n"
                                  u"3、点击导入按钮,将Config_file文件夹下IP对应的参数文件导入设备\r\n"
                                  u"③批量开IE：\r\n"                                  
                                  u"1、进入对应的Sheet页,填写参数\r\n"
                                  u"2、需要保证IE浏览器的缩放为100%\r\n"
                                  u"④批量导入NVR：\r\n"
                                  u"1、进入对应进入对应的Sheet页,填写参数\r\n"
                                  u"2、设备加入NVR后，通道命令规则为'设备IP-通道号'，如10.65.71.155-1\r\n"
                                  u"3、协议需选择对应协议，若选择GB28181，则将该设备放于最后一个，涉及NVR重启")

        # 水平盒式布局
        layout = QGridLayout()

        # 添加控件
        layout.addWidget(self.label_1, 0, 0)
        layout.addWidget(self.label_2, 0, 8)
        layout.addWidget(self.label_3, 1, 0)
        layout.addWidget(self.label_4, 1, 8)
        layout.addWidget(self.label_5, 2, 0)
        layout.addWidget(self.label_6, 3, 0)
        layout.addWidget(self.button_cfg_out, 0, 1, 1, 7)
        layout.addWidget(self.button_cfg_in, 0, 9, 1, 7)
        layout.addWidget(self.button_ie, 1, 1, 1, 7)
        layout.addWidget(self.button_format, 1, 9, 1, 7)
        layout.addWidget(self.button_excel, 2, 9, 1, 7)
        layout.addWidget(self.button_report, 3, 9, 1, 7)
        layout.addWidget(self.button_nvr, 2, 1, 1, 7)
        layout.addWidget(self.button_bohao, 3, 1, 1, 7)
        layout.addWidget(self.label_time1, 1, 17)
        layout.addWidget(self.label_time2, 1, 18)
        layout.addWidget(self.label_msg, 4, 0)
        layout.addWidget(self.process, 4, 1, 2, 7)
        layout.addWidget(self.label_result, 4, 8)
        layout.addWidget(self.QTextBrowser, 4, 9, 2, 7)

        # 设置布局
        self.setLayout(layout)

        # 工具标题
        self.setWindowTitle(u"稳定性工具合集")

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

    # 批量开IE按钮所对应的执行流程
    def ie(self):
        # 清空各个输出框的信息
        self.QTextBrowser.setPlainText("")
        self.process.setText("")
        self.label_time2.setText("0")
        # 将打印输出到日志打印控件
        sys.stdout = Stream(newText=self.onUpdateText)

        self.my_thread.is_on = True
        self.my_thread.start()

        self.thread = IeThread()
        self.thread.trigger.connect(self.ie_ride)
        self.thread.start()

    # 参数导出按钮所对应的执行流程
    def cfg_out(self):
        # 清空各个输出框的信息
        self.QTextBrowser.setPlainText("")
        self.process.setText("")
        self.label_time2.setText("0")
        # 将打印输出到日志打印控件
        sys.stdout = Stream(newText=self.onUpdateText)

        self.my_thread.is_on = True
        self.my_thread.start()

        self.thread = Cfg_out_Thread()
        self.thread.trigger.connect(self.cfg_out_ride)
        self.thread.start()

    # 大面积格式化按钮所对应的执行流程
    def format(self):
        # 清空各个输出框的信息
        self.QTextBrowser.setPlainText("")
        self.process.setText("")
        self.label_time2.setText("0")
        # 将打印输出到日志打印控件
        sys.stdout = Stream(newText=self.onUpdateText)

        self.my_thread.is_on = True
        self.my_thread.start()

        self.thread = Format_Thread()
        self.thread.trigger.connect(self.format_ride)
        self.thread.start()

    # 参数导入按钮所对应的执行流程
    def cfg_in(self):
        # 清空各个输出框的信息
        self.QTextBrowser.setPlainText("")
        self.process.setText("")
        self.label_time2.setText("0")
        # 将打印输出到日志打印控件
        sys.stdout = Stream(newText=self.onUpdateText)

        self.my_thread.is_on = True
        self.my_thread.start()

        self.thread = Cfg_in_Thread()
        self.thread.trigger.connect(self.cfg_in_ride)
        self.thread.start()

    # 批量导入NVR按钮所对应的执行流程
    def nvr(self):
        # 清空各个输出框的信息
        self.QTextBrowser.setPlainText("")
        self.process.setText("")
        self.label_time2.setText("0")
        # 将打印输出到日志打印控件
        sys.stdout = Stream(newText=self.onUpdateText)

        self.my_thread.is_on = True
        self.my_thread.start()

        self.thread = NvrThread()
        self.thread.trigger.connect(self.nvr_ride)
        self.thread.start()

    # 批量导入NVR按钮所对应的执行流程
    def bohao(self):
        # 清空各个输出框的信息
        self.QTextBrowser.setPlainText("")
        self.process.setText("")
        self.label_time2.setText("0")
        # 将打印输出到日志打印控件
        sys.stdout = Stream(newText=self.onUpdateText)

        self.my_thread.is_on = True
        self.my_thread.start()

        self.thread = BohaoThread()
        self.thread.trigger.connect(self.bohao_ride)
        self.thread.start()

    # 打开Excel按钮
    def excel(self):
        # 清空各个输出框的信息
        try:
            os.startfile(u'devices\devices.xlsx')
        except Exception as e:
            QMessageBox.information(self, u"提示", u"打开文件失败", QMessageBox.Yes)

    # 打开报告按钮
    def report(self):
        # 清空各个输出框的信息
        try:
            file_all = sort_file_by_time('devices')
            file = []
            for i in file_all:
                if 'report' in i:
                    file.append(i)
            os.startfile(u'devices\\' +  file[-1])
        except Exception as e:
            QMessageBox.information(self, u"提示", u"打开文件失败，请手动检查", QMessageBox.Yes)

    # 批量IE按钮执行完毕后进行数据回填
    def ie_ride(self, result):
        try:
            # 停止计时器
            self.my_thread.is_on = False
            self.QTextBrowser.append(u"执行结果见左侧日志打印")
            QMessageBox.information(self, u"提示", u"执行完毕，请查看结果", QMessageBox.Yes)
        except Exception as e:
            self.my_thread.is_on = False
            QMessageBox.information(self, u"提示", u"执行出错，请检查填写的参数与设备本身", QMessageBox.Yes)

    # 参数导出按钮执行完毕后进行数据回填
    def cfg_out_ride(self, result):
        try:
            # 停止计时器
            self.my_thread.is_on = False
            self.QTextBrowser.append(u"执行失败的设备信息如下:")
            for i in result:
                self.QTextBrowser.append(i)
            QMessageBox.information(self, u"提示", u"执行完毕，请查看结果", QMessageBox.Yes)
        except Exception as e:
            self.my_thread.is_on = False
            QMessageBox.information(self, u"提示", u"执行出错，请检查填写的参数与设备本身", QMessageBox.Yes)

    # 参数导入按钮执行完毕后进行数据回填
    def cfg_in_ride(self, result):
        try:
            # 停止计时器
            self.my_thread.is_on = False
            self.QTextBrowser.append(u"执行失败的设备信息如下:")
            for i in result:
                self.QTextBrowser.append(i)
            QMessageBox.information(self, u"提示", u"执行完毕，请查看结果", QMessageBox.Yes)
        except Exception as e:
            self.my_thread.is_on = False
            QMessageBox.information(self, u"提示", u"执行出错，请检查填写的参数与设备本身", QMessageBox.Yes)

    # 大面积格式化按钮执行完毕后进行数据回填
    def format_ride(self, result):
        try:
            # 停止计时器
            self.my_thread.is_on = False
            self.QTextBrowser.append(u"执行结果如下:")
            for i in result:
                self.QTextBrowser.append(i)
            QMessageBox.information(self, u"提示", u"执行完毕，请查看结果", QMessageBox.Yes)
        except Exception as e:
            self.my_thread.is_on = False
            QMessageBox.information(self, u"提示", u"执行出错，请检查填写的参数与设备本身", QMessageBox.Yes)

    # 大面积格式化按钮执行完毕后进行数据回填
    def nvr_ride(self, result):
        try:
            # 停止计时器
            self.my_thread.is_on = False
            self.QTextBrowser.append(u"执行失败的设备信息如下:")
            for i in result:
                if i != u'':
                    self.QTextBrowser.append(i)
            QMessageBox.information(self, u"提示", u"执行完毕，请查看结果", QMessageBox.Yes)
        except Exception as e:
            self.my_thread.is_on = False
            QMessageBox.information(self, u"提示", u"执行出错，请检查填写的参数与设备本身", QMessageBox.Yes)

    # 大面积格式化按钮执行完毕后进行数据回填
    def bohao_ride(self, result):
        try:
            # 停止计时器
            self.my_thread.is_on = False
            self.QTextBrowser.append(u"执行结果如下:")
            for i in result:
                if i != u'':
                    self.QTextBrowser.append(i)
            QMessageBox.information(self, u"提示", u"执行完毕，请查看结果", QMessageBox.Yes)
        except Exception as e:
            self.my_thread.is_on = False
            QMessageBox.information(self, u"提示", u"执行出错，请检查填写的参数与设备本身", QMessageBox.Yes)

    # 计时器更新
    def set_label_func(self, num):
        self.label_time2.setText(num)


# 业务执行-子线程
class IeThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(list)

    # 初始化数据
    def __init__(self):
        super(IeThread, self).__init__()

    # 处理业务逻辑
    def run(self):
        self.ie = open_device.open_device()
        self.trigger.emit(self.ie)

# 业务执行-子线程
class Cfg_out_Thread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(list)

    # 初始化数据
    def __init__(self):
        super(Cfg_out_Thread, self).__init__()

    # 处理业务逻辑
    def run(self):
        self.cfg_out = cfg_tool.cfg(u'导出')
        self.trigger.emit(self.cfg_out)

# 业务执行-子线程
class Cfg_in_Thread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(list)

    # 初始化数据
    def __init__(self):
        super(Cfg_in_Thread, self).__init__()

    # 处理业务逻辑
    def run(self):
        self.cfg_in = cfg_tool.cfg(u'导入')
        self.trigger.emit(self.cfg_in)

# 业务执行-子线程
class Format_Thread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(list)

    # 初始化数据
    def __init__(self):
        super(Format_Thread, self).__init__()

    # 处理业务逻辑
    def run(self):
        self.format = format_stability.format_stability()
        self.trigger.emit(self.format)

# 业务执行-子线程
class NvrThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(list)

    # 初始化数据
    def __init__(self):
        super(NvrThread, self).__init__()

    # 处理业务逻辑
    def run(self):
        self.nvr = NVR_Tool.NVR_ADD()
        self.trigger.emit(self.nvr)

# 业务执行-子线程
class BohaoThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(list)

    # 初始化数据
    def __init__(self):
        super(BohaoThread, self).__init__()

    # 处理业务逻辑
    def run(self):
        self.bohao = bohao_check.bohao_check()
        self.trigger.emit(self.bohao)



# 计时器-子线程
class TimeThread(QtCore.QThread):  # 线程类
    my_signal = QtCore.pyqtSignal(str)  # 自定义信号对象。参数str就代表这个信号可以传一个字符串

    def __init__(self):
        super(TimeThread, self).__init__()
        self.count = 0
        self.is_on = True

    # 运行计时器
    def run(self):
        while self.is_on:
            self.count += 1
            self.my_signal.emit(str(self.count))  # 释放自定义的信号
            self.sleep(1)  # 本线程睡眠1秒，即计时作用

