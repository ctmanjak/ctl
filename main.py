# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from macroform import macroForm
from loginform import loginForm
import ctl
import time

class WindowControl(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ctl = ctl.CtlMacro()
        self.init()

    def init(self):
        self.loginForm = loginForm(self)
        self.loginForm.show()
        self.loginForm.exec_()
        if not self.loginForm.ltinfo[0] == False:
            self.macroForm = macroForm(self)
            self.macroForm.setupUi()
            self.macroForm.btn_logout.clicked.connect(self.logout)
            for ltinfo in self.loginForm.ltinfo:
                tmp = QtWidgets.QListWidgetItem(ltinfo[0])
                tmp.setData(3, ltinfo)
                self.macroForm.ltw_main.addItem(tmp)
                self.macroForm.ltw_main.setCurrentRow(0)
            self.macroForm.show()
        del self.loginForm
        pass

    def logout(self):
        self.macroForm.lecture_stop()
        self.macroForm.lecture_stop()
        del self.macroForm
        self.ctl.init()
        self.ctl.reloadSession()
        self.init()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    WindowControl = WindowControl()
    sys.exit(app.exec_())
