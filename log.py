# -*- coding: utf-8 -*-
from PyQt4 import QtCore
import sys
reload(sys)
sys.setdefaultencoding('utf8')


# 日志输出
class Stream(QtCore.QObject):
    # 重定向控制台输出到文本框
    newText = QtCore.pyqtSignal(str)

    # 发送信号给槽函数
    def write(self, text):
        self.newText.emit(unicode(str(text)))