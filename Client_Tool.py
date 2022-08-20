# -*- coding: utf-8 -*-
from PyQt4.QtGui import QPushButton, QWidget, QLabel, QApplication, QGridLayout, QTextBrowser, QMessageBox, QFont,QTextCursor,QTextEdit
from PyQt4 import QtCore
import Create_ClientDemo_CfgFile_Tool
import os
import sys
from log import Stream


# GUI界面函数
class GUI(QWidget):
    def __init__(self, parent=None):
        super(GUI, self).__init__(parent)

        # 初始化GUI界面
        self.setup_ui()

        # 实例化计时器子线程对象
        self.my_thread = TimeThread()
        self.my_thread.my_signal.connect(self.set_label_func)


        # 按钮响应
        self.button_client.clicked.connect(self.client)
        self.button_excel.clicked.connect(self.excel)
        self.button_file.clicked.connect(self.file)

    def setup_ui(self):

        self.label_1 = QLabel(u"ClientDemo")

        # 执行按钮控件
        self.button_client = QPushButton(u"ClientDemo配置文件生成")
        self.button_excel = QPushButton(u"打开devices.xlsx进行配置")
        self.button_file = QPushButton(u"打开ClientDemo配置文件所在文件夹")

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
        self.process.setPlainText(u"生成ClientDemo配置文件，可批量对Demo设备进行配置\r\n"
                                  u"1、点击按钮直接打开devices.xlsx，进入对应的Sheet页，填写参数\r\n"
                                  u"2、如果需要添加多台相同IP设备,请将开启多通道支持选择为F\r\n"
                                  u"3、点击按钮执行，成功后会在文件夹devices下会生成1个json\r\n"
                                  u"4、点击按钮直接进入Json文件所在文件夹，拷贝json至Demo目录")

        # 水平盒式布局
        layout = QGridLayout()

        # 添加控件
        layout.addWidget(self.label_1, 0, 0)
        layout.addWidget(self.button_client, 0, 1, 1, 7)
        layout.addWidget(self.button_excel, 1, 1, 1, 7)
        layout.addWidget(self.button_file, 2, 1, 1, 7)
        layout.addWidget(self.label_time1, 2, 8)
        layout.addWidget(self.label_time2, 2, 9)
        layout.addWidget(self.label_msg, 3, 0)
        layout.addWidget(self.process, 3, 1, 2, 7)
        layout.addWidget(self.label_result, 3, 8)
        layout.addWidget(self.QTextBrowser, 3, 9, 2, 7)

        # 设置布局
        self.setLayout(layout)

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

    # 执行按钮逻辑
    def client(self):
        # 清空各个输出框的信息
        self.QTextBrowser.setPlainText("")
        self.process.setText("")
        self.label_time2.setText("0")
        # 将打印输出到日志打印控件
        sys.stdout = Stream(newText=self.onUpdateText)

        self.my_thread.is_on = True
        self.my_thread.start()

        self.thread = ClientThread()
        self.thread.trigger.connect(self.client_ride)
        self.thread.start()

    # 打开Excel
    def excel(self):
        # 清空各个输出框的信息
        try:
            os.startfile(u'devices\devices.xlsx')
        except Exception as e:
            QMessageBox.information(self, u"提示", u"打开文件失败", QMessageBox.Yes)

    # 打开文件夹
    def file(self):
        # 清空各个输出框的信息
        try:
            os.startfile(u'devices')
        except Exception as e:
            QMessageBox.information(self, u"提示", u"打开文件夹失败", QMessageBox.Yes)

    # 执行子线程函数结束后进行数据回填
    def client_ride(self):
        try:
            # 停止计时器
            self.QTextBrowser.append(u"执行结果：")
            self.QTextBrowser.append(u"执行完毕")
            self.my_thread.is_on = False

            QMessageBox.information(self, u"提示", u"执行完毕，请查看结果", QMessageBox.Yes)
        except Exception as e:
            self.my_thread.is_on = False
            QMessageBox.information(self, u"提示", u"执行出错，请检查填写的参数与设备本身", QMessageBox.Yes)

    # 计时器更新
    def set_label_func(self, num):
        self.label_time2.setText(num)


# 业务执行-子线程
class ClientThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal()

    # 初始化数据
    def __init__(self):
        super(ClientThread, self).__init__()

    # 处理业务逻辑
    def run(self):
        self.client = Create_ClientDemo_CfgFile_Tool.Client()
        self.trigger.emit()

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = GUI()
    GUI.show()
    sys.exit(app.exec_())