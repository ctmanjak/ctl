from PyQt5 import QtCore, QtGui, QtWidgets

class loginForm(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setupUi()
        #self.show()

    def setupUi(self):
        self.id = None
        self.password = None
        self.ltinfo = [False]
        self.setObjectName("MainWindow")
        self.resize(272, 109)
        self.lineEdit = QtWidgets.QLineEdit( self)
        self.lineEdit.setGeometry(QtCore.QRect(30, 30, 113, 20))
        self.lineEdit_2 = QtWidgets.QLineEdit(self)
        self.lineEdit_2.setGeometry(QtCore.QRect(30, 60, 113, 20))
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(170, 30, 75, 51))
        self.retranslateUi()
        self.pushButton.clicked.connect(self.login)
        
        #layout.addWidget(self.lineEdit)

    def login(self):
        self.id = self.lineEdit.text()
        self.password = self.lineEdit_2.text()
        self.pushButton.setEnabled(False)
        self.ltinfo = self.parent.ctl.findlecture(self.id, self.password)
        if self.ltinfo[0] == False:
            if self.ltinfo[1] == "login":
                msgbox = QtWidgets.QMessageBox(self)
                msgbox.warning(self, "로그인 실패", "로그인 실패")
            elif self.ltinfo[1] == "lecture":
                msgbox = QtWidgets.QMessageBox(self)
                msgbox.warning(self, "들을 강의 없음", "들을 강의 없음")
            self.parent.ctl.reloadSession()
            self.pushButton.setEnabled(True)
        else:self.close()


    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "인강 매크로"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "학번"))
        self.lineEdit_2.setPlaceholderText(_translate("MainWindow", "비번"))
        self.pushButton.setText(_translate("MainWindow", "로그인"))
