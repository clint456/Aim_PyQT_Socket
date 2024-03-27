# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'GUI.ui'
##
## Created by: Qt User Interface Compiler version 6.4.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGroupBox, QLabel, QPushButton,
    QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(962, 766)
        self.pictureLabel = QLabel(Form)
        self.pictureLabel.setObjectName(u"pictureLabel")
        self.pictureLabel.setGeometry(QRect(10, 60, 941, 541))
        self.pictureLabel.setCursor(QCursor(Qt.CrossCursor))
        self.pictureLabel.setMouseTracking(True)
        self.pictureLabel.setContextMenuPolicy(Qt.NoContextMenu)
        self.pictureLabel.setAutoFillBackground(False)
        self.pictureLabel.setStyleSheet(u"ui->label->setStyleSheet(\"QLabel{background:#000000;}\"); ")
        self.pictureLabel.setWordWrap(False)
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(30, 30, 72, 15))
        self.label_2.setMouseTracking(True)
        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(230, 620, 501, 131))
        self.pushButton_aim = QPushButton(self.groupBox)
        self.pushButton_aim.setObjectName(u"pushButton_aim")
        self.pushButton_aim.setGeometry(QRect(30, 30, 151, 71))
        self.pushButton_shot = QPushButton(self.groupBox)
        self.pushButton_shot.setObjectName(u"pushButton_shot")
        self.pushButton_shot.setGeometry(QRect(290, 30, 151, 71))
        self.playButton = QPushButton(Form)
        self.playButton.setObjectName(u"playButton")
        self.playButton.setGeometry(QRect(120, 20, 93, 28))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pictureLabel.setText("")
        self.label_2.setText(QCoreApplication.translate("Form", u"\u4e91\u53f0\u753b\u9762", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"Groupbox", None))
        self.pushButton_aim.setText(QCoreApplication.translate("Form", u"\u7784\u51c6", None))
        self.pushButton_shot.setText(QCoreApplication.translate("Form", u"\u5f00\u706b", None))
        self.playButton.setText("")
    # retranslateUi

