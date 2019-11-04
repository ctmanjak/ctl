from PyQt5 import QtCore, QtGui, QtWidgets
import ctl, threading, time, datetime

class macroForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.pgbArray = []

    def setupUi(self):
        grid = QtWidgets.QGridLayout()
        self.setLayout(grid)
        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setObjectName("groupBox")
        self.ltw_main = QtWidgets.QListWidget(self.groupBox)
        self.ltw_main.setObjectName("ltw_main")
        self.btn_start = QtWidgets.QPushButton(self)
        self.btn_start.setObjectName("btn_start")
        self.btn_stop = QtWidgets.QPushButton(self)
        self.btn_stop.setObjectName("btn_stop")
        self.btn_logout = QtWidgets.QPushButton(self)
        self.btn_logout.setObjectName("btn_logout")
        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.hide()

        self.ltw_main.itemSelectionChanged.connect(self.selectchange)

        self.btn_start.clicked.connect(self.lecture_start)
        self.btn_stop.clicked.connect(self.lecture_stop)

        groupBoxLayout = QtWidgets.QGridLayout()
        groupBoxLayout.addWidget(self.ltw_main, 0, 0)
        self.groupBox.setLayout(groupBoxLayout)
        grid.setRowMinimumHeight(0, 250)
        grid.setColumnMinimumWidth(0, 100)
        grid.setColumnMinimumWidth(1, 100)
        grid.setColumnMinimumWidth(2, 100)

        grid.addWidget(self.groupBox, 0, 0, 1, 3)
        grid.addWidget(self.btn_start, 1, 0)
        grid.addWidget(self.btn_stop, 1, 1)
        grid.addWidget(self.btn_logout, 1, 2)
        grid.addWidget(self.line, 2, 0, 1, 3)

        self.retranslateUi()
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def selectchange(self):
        print(self.ltw_main.selectedItems()[0].data(3))

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "인강 매크로"))
        self.groupBox.setTitle(_translate("MainWindow", "강의목록"))
        self.btn_start.setText(_translate("MainWindow", "강의시작"))
        self.btn_stop.setText(_translate("MainWindow", "그만듣기"))
        self.btn_logout.setText(_translate("MainWindow", "로그아웃"))

    def makeProgress(self):
        self.pgbArray = []
        self.line.show()
        #self.layout().addWidget(self.line, 2, 0, 1, 3)
        for progress in self.parent.ctl.progress:
            self.pgbArray.append(QtWidgets.QProgressBar())
            self.pgbArray[len(self.pgbArray)-1].setValue(0)
            self.layout().addWidget(self.pgbArray[len(self.pgbArray)-1], 3 + (len(self.pgbArray)-1), 0, 1, 3)
        self.parent.ctl.make_progress.connect(self._makeProgress)
        self.parent.ctl.change_progress.connect(self.chkProgress)

    def _makeProgress(self, id):
        self.pgbArray[id].setMaximum(self.parent.ctl.progress[id]["basictime"])

    def chkProgress(self, id, progress):
        if not progress == -1:
            self.pgbArray[id].setValue(progress)
            self.pgbArray[id].setFormat("{0} / {1}".format(datetime.timedelta(seconds=self.pgbArray[id].value()), datetime.timedelta(seconds=self.pgbArray[id].maximum())))
        else:
            self.pgbArray[id].setFormat("END")

            if self.parent.ctl.currentnum < 1:
                self.lecture_stop()

    def lecture_start(self):
        data = self.parent.ctl.getlectures(self.ltw_main.selectedItems()[0].data(3))
        self.parent.ctl.quitmsg = ""
        self.threads = []
        for ltdata in data["ltdata"]:
            self.threads.append(threading.Thread(target=self.parent.ctl.test2, args=(data["ltinfo"], ltdata)))

        for t in self.threads:
            t.start()

        while(not len(self.parent.ctl.progress) == len(data["ltdata"])): pass
        else:
            self.makeProgress()
            self.parent.ctl.cond.wakeAll()

    def lecture_stop(self):
        if len(self.pgbArray) > 0:
            self.parent.ctl.quitmsg = "q"
            for t in self.threads:
                t.join()
            for pgb in self.pgbArray:
                self.layout().removeWidget(pgb)
                pgb.deleteLater()
                del pgb
            self.line.hide()
            self.parent.ctl.init()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = macroForm()
    ui.setupUi()
    ui.show()
    sys.exit(app.exec_())
