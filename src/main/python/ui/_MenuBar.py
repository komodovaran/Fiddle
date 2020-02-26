# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '_MenuBar.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MenuBar(object):
    def setupUi(self, MenuBar):
        MenuBar.setObjectName("MenuBar")
        MenuBar.resize(500, 500)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MenuBar.sizePolicy().hasHeightForWidth())
        MenuBar.setSizePolicy(sizePolicy)
        MenuBar.setMinimumSize(QtCore.QSize(500, 500))
        MenuBar.setMaximumSize(QtCore.QSize(5000, 5000))
        MenuBar.setFocusPolicy(QtCore.Qt.ClickFocus)
        MenuBar.setWindowTitle("")
        MenuBar.setStatusTip("")
        MenuBar.setWhatsThis("")
        MenuBar.setAccessibleName("")
        MenuBar.setAutoFillBackground(False)
        MenuBar.setStyleSheet("")
        MenuBar.setDocumentMode(False)
        MenuBar.setDockNestingEnabled(False)
        MenuBar.setUnifiedTitleAndToolBarOnMac(False)
        self.centralWidget = QtWidgets.QWidget(MenuBar)
        self.centralWidget.setStyleSheet("background rgb(0,0,0)")
        self.centralWidget.setObjectName("centralWidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout_2.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_2.setSpacing(6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        MenuBar.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MenuBar)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 500, 22))
        self.menuBar.setNativeMenuBar(True)
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        MenuBar.setMenuBar(self.menuBar)
        self.menuFile.addSeparator()
        self.menuFile.addSeparator()
        self.menuBar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MenuBar)
        QtCore.QMetaObject.connectSlotsByName(MenuBar)

    def retranslateUi(self, MenuBar):
        _translate = QtCore.QCoreApplication.translate
        self.menuFile.setTitle(_translate("MenuBar", "File"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MenuBar = QtWidgets.QMainWindow()
    ui = Ui_MenuBar()
    ui.setupUi(MenuBar)
    MenuBar.show()
    sys.exit(app.exec_())
