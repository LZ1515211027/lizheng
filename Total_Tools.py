# -*- coding: utf-8 -*-
from PyQt4.QtGui import QApplication, QTabWidget, QFont
import sys
import ONVIF_Tool
import Stability_Tool
import Client_Tool
import Format_Tool
import SADP_Tool


class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        self.Onvif_Content = ONVIF_Tool.GUI()
        self.Stability_Content = Stability_Tool.GUI()
        self.Client_Content = Client_Tool.GUI()
        self.FormatGui_Content = Format_Tool.GUI()
        self.SADP_Content = SADP_Tool.GUI()

        self.addTab(self.Stability_Content, u"稳定性工具")
        self.addTab(self.Client_Content, u"ClientDemo配置文件生成")
        self.addTab(self.SADP_Content, u"SADP激活/HEOP获取")
        self.addTab(self.Onvif_Content, u"ONVIF参数配置")
        self.addTab(self.FormatGui_Content, u"功能测试-格式化相关")

        self.setWindowTitle(u"lizheng19工具合集")
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setMinimumSize(600, 450)
        self.setMaximumSize(1200, 800)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    t = TabWidget()
    t.show()
    app.exec_()