# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ch09_form.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_ProfileForm(object):
    def setupUi(self, ProfileForm):
        if not ProfileForm.objectName():
            ProfileForm.setObjectName(u"ProfileForm")
        ProfileForm.resize(420, 240)
        self.rootLayout = QVBoxLayout(ProfileForm)
        self.rootLayout.setObjectName(u"rootLayout")
        self.rootLayout.setContentsMargins(18, 16, 18, 16)
        self.headingLabel = QLabel(ProfileForm)
        self.headingLabel.setObjectName(u"headingLabel")
        self.headingLabel.setStyleSheet(u"font-size: 16px; font-weight: bold;")

        self.rootLayout.addWidget(self.headingLabel)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.nameCaption = QLabel(ProfileForm)
        self.nameCaption.setObjectName(u"nameCaption")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.nameCaption)

        self.nameEdit = QLineEdit(ProfileForm)
        self.nameEdit.setObjectName(u"nameEdit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.nameEdit)

        self.planCaption = QLabel(ProfileForm)
        self.planCaption.setObjectName(u"planCaption")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.planCaption)

        self.planCombo = QComboBox(ProfileForm)
        self.planCombo.addItem("")
        self.planCombo.addItem("")
        self.planCombo.addItem("")
        self.planCombo.setObjectName(u"planCombo")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.planCombo)


        self.rootLayout.addLayout(self.formLayout)

        self.agreeCheck = QCheckBox(ProfileForm)
        self.agreeCheck.setObjectName(u"agreeCheck")

        self.rootLayout.addWidget(self.agreeCheck)

        self.buttonRow = QHBoxLayout()
        self.buttonRow.setObjectName(u"buttonRow")
        self.buttonSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonRow.addItem(self.buttonSpacer)

        self.submitButton = QPushButton(ProfileForm)
        self.submitButton.setObjectName(u"submitButton")

        self.buttonRow.addWidget(self.submitButton)


        self.rootLayout.addLayout(self.buttonRow)

        self.resultLabel = QLabel(ProfileForm)
        self.resultLabel.setObjectName(u"resultLabel")

        self.rootLayout.addWidget(self.resultLabel)

        self.bottomSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.rootLayout.addItem(self.bottomSpacer)


        self.retranslateUi(ProfileForm)

        QMetaObject.connectSlotsByName(ProfileForm)
    # setupUi

    def retranslateUi(self, ProfileForm):
        ProfileForm.setWindowTitle(QCoreApplication.translate("ProfileForm", u"Qt Designer \u3067\u4f5c\u3063\u305f\u30d5\u30a9\u30fc\u30e0", None))
        self.headingLabel.setText(QCoreApplication.translate("ProfileForm", u"\u304a\u7533\u3057\u8fbc\u307f", None))
        self.nameCaption.setText(QCoreApplication.translate("ProfileForm", u"\u304a\u540d\u524d", None))
        self.nameEdit.setPlaceholderText(QCoreApplication.translate("ProfileForm", u"\u5c71\u7530 \u592a\u90ce", None))
        self.planCaption.setText(QCoreApplication.translate("ProfileForm", u"\u30d7\u30e9\u30f3", None))
        self.planCombo.setItemText(0, QCoreApplication.translate("ProfileForm", u"\u7121\u6599\u30d7\u30e9\u30f3", None))
        self.planCombo.setItemText(1, QCoreApplication.translate("ProfileForm", u"\u6a19\u6e96\u30d7\u30e9\u30f3", None))
        self.planCombo.setItemText(2, QCoreApplication.translate("ProfileForm", u"\u4e0a\u4f4d\u30d7\u30e9\u30f3", None))

        self.agreeCheck.setText(QCoreApplication.translate("ProfileForm", u"\u5229\u7528\u898f\u7d04\u306b\u540c\u610f\u3059\u308b", None))
        self.submitButton.setText(QCoreApplication.translate("ProfileForm", u"\u9001\u4fe1", None))
        self.resultLabel.setText(QCoreApplication.translate("ProfileForm", u"\u307e\u3060\u9001\u4fe1\u3055\u308c\u3066\u3044\u307e\u305b\u3093", None))
    # retranslateUi

