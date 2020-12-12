# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(818, 678)
        font = QtGui.QFont()
        font.setPointSize(16)
        MainWindow.setFont(font)
        self.central_widget = QtWidgets.QWidget(MainWindow)
        self.central_widget.setObjectName("central_widget")
        self.gridLayout = QtWidgets.QGridLayout(self.central_widget)
        self.gridLayout.setObjectName("gridLayout")
        self.stacked_widget = QtWidgets.QStackedWidget(self.central_widget)
        self.stacked_widget.setObjectName("stacked_widget")
        self.mode_page = QtWidgets.QWidget()
        self.mode_page.setObjectName("mode_page")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.mode_page)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.mode_page_layout = QtWidgets.QGridLayout()
        self.mode_page_layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.mode_page_layout.setObjectName("mode_page_layout")
        self.receiver_button = QtWidgets.QPushButton(self.mode_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.receiver_button.sizePolicy().hasHeightForWidth())
        self.receiver_button.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.receiver_button.setFont(font)
        self.receiver_button.setStyleSheet("")
        self.receiver_button.setObjectName("receiver_button")
        self.mode_page_layout.addWidget(self.receiver_button, 1, 1, 1, 1)
        self.sender_button = QtWidgets.QPushButton(self.mode_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sender_button.sizePolicy().hasHeightForWidth())
        self.sender_button.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.sender_button.setFont(font)
        self.sender_button.setStyleSheet("")
        self.sender_button.setObjectName("sender_button")
        self.mode_page_layout.addWidget(self.sender_button, 1, 0, 1, 1)
        self.sender_label = QtWidgets.QLabel(self.mode_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sender_label.sizePolicy().hasHeightForWidth())
        self.sender_label.setSizePolicy(sizePolicy)
        self.sender_label.setText("")
        self.sender_label.setPixmap(QtGui.QPixmap(":/icons/Sender.png"))
        self.sender_label.setScaledContents(True)
        self.sender_label.setObjectName("sender_label")
        self.mode_page_layout.addWidget(self.sender_label, 0, 0, 1, 1)
        self.receiver_label = QtWidgets.QLabel(self.mode_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.receiver_label.sizePolicy().hasHeightForWidth())
        self.receiver_label.setSizePolicy(sizePolicy)
        self.receiver_label.setText("")
        self.receiver_label.setPixmap(QtGui.QPixmap(":/icons/Receiver.png"))
        self.receiver_label.setScaledContents(True)
        self.receiver_label.setObjectName("receiver_label")
        self.mode_page_layout.addWidget(self.receiver_label, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.mode_page_layout, 0, 0, 1, 1)
        self.stacked_widget.addWidget(self.mode_page)
        self.param_page = QtWidgets.QWidget()
        self.param_page.setObjectName("param_page")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.param_page)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.param_page_layout = QtWidgets.QGridLayout()
        self.param_page_layout.setObjectName("param_page_layout")
        self.timeout_slider = QtWidgets.QSlider(self.param_page)
        self.timeout_slider.setMinimum(1)
        self.timeout_slider.setMaximum(5000)
        self.timeout_slider.setPageStep(50)
        self.timeout_slider.setProperty("value", 500)
        self.timeout_slider.setOrientation(QtCore.Qt.Horizontal)
        self.timeout_slider.setObjectName("timeout_slider")
        self.param_page_layout.addWidget(self.timeout_slider, 5, 1, 1, 1)
        self.timeout_value_label = QtWidgets.QLabel(self.param_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timeout_value_label.sizePolicy().hasHeightForWidth())
        self.timeout_value_label.setSizePolicy(sizePolicy)
        self.timeout_value_label.setMinimumSize(QtCore.QSize(64, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.timeout_value_label.setFont(font)
        self.timeout_value_label.setAlignment(QtCore.Qt.AlignCenter)
        self.timeout_value_label.setObjectName("timeout_value_label")
        self.param_page_layout.addWidget(self.timeout_value_label, 5, 2, 1, 1)
        self.path_button = QtWidgets.QPushButton(self.param_page)
        self.path_button.setMinimumSize(QtCore.QSize(140, 0))
        self.path_button.setText("")
        self.path_button.setObjectName("path_button")
        self.param_page_layout.addWidget(self.path_button, 6, 2, 1, 1)
        self.start_button = QtWidgets.QPushButton(self.param_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.start_button.sizePolicy().hasHeightForWidth())
        self.start_button.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.start_button.setFont(font)
        self.start_button.setObjectName("start_button")
        self.param_page_layout.addWidget(self.start_button, 9, 2, 1, 1)
        self.packet_loss_chance_value_label = QtWidgets.QLabel(self.param_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.packet_loss_chance_value_label.sizePolicy().hasHeightForWidth())
        self.packet_loss_chance_value_label.setSizePolicy(sizePolicy)
        self.packet_loss_chance_value_label.setMinimumSize(QtCore.QSize(64, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.packet_loss_chance_value_label.setFont(font)
        self.packet_loss_chance_value_label.setAlignment(QtCore.Qt.AlignCenter)
        self.packet_loss_chance_value_label.setObjectName("packet_loss_chance_value_label")
        self.param_page_layout.addWidget(self.packet_loss_chance_value_label, 3, 2, 1, 1)
        self.window_size_slider = QtWidgets.QSlider(self.param_page)
        self.window_size_slider.setMinimum(1)
        self.window_size_slider.setMaximum(1024)
        self.window_size_slider.setSingleStep(1)
        self.window_size_slider.setPageStep(32)
        self.window_size_slider.setProperty("value", 32)
        self.window_size_slider.setOrientation(QtCore.Qt.Horizontal)
        self.window_size_slider.setObjectName("window_size_slider")
        self.param_page_layout.addWidget(self.window_size_slider, 2, 1, 1, 1)
        self.packet_size_value_label = QtWidgets.QLabel(self.param_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.packet_size_value_label.sizePolicy().hasHeightForWidth())
        self.packet_size_value_label.setSizePolicy(sizePolicy)
        self.packet_size_value_label.setMinimumSize(QtCore.QSize(64, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.packet_size_value_label.setFont(font)
        self.packet_size_value_label.setAlignment(QtCore.Qt.AlignCenter)
        self.packet_size_value_label.setObjectName("packet_size_value_label")
        self.param_page_layout.addWidget(self.packet_size_value_label, 0, 2, 1, 1)
        self.packet_size_label = QtWidgets.QLabel(self.param_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.packet_size_label.sizePolicy().hasHeightForWidth())
        self.packet_size_label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.packet_size_label.setFont(font)
        self.packet_size_label.setAlignment(QtCore.Qt.AlignCenter)
        self.packet_size_label.setObjectName("packet_size_label")
        self.param_page_layout.addWidget(self.packet_size_label, 0, 0, 1, 1)
        self.packet_corruption_chance_label = QtWidgets.QLabel(self.param_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.packet_corruption_chance_label.sizePolicy().hasHeightForWidth())
        self.packet_corruption_chance_label.setSizePolicy(sizePolicy)
        self.packet_corruption_chance_label.setAlignment(QtCore.Qt.AlignCenter)
        self.packet_corruption_chance_label.setObjectName("packet_corruption_chance_label")
        self.param_page_layout.addWidget(self.packet_corruption_chance_label, 4, 0, 1, 1)
        self.path_label = QtWidgets.QLabel(self.param_page)
        self.path_label.setText("")
        self.path_label.setAlignment(QtCore.Qt.AlignCenter)
        self.path_label.setObjectName("path_label")
        self.param_page_layout.addWidget(self.path_label, 6, 0, 1, 1)
        self.packet_loss_chance_label = QtWidgets.QLabel(self.param_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.packet_loss_chance_label.sizePolicy().hasHeightForWidth())
        self.packet_loss_chance_label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.packet_loss_chance_label.setFont(font)
        self.packet_loss_chance_label.setAlignment(QtCore.Qt.AlignCenter)
        self.packet_loss_chance_label.setObjectName("packet_loss_chance_label")
        self.param_page_layout.addWidget(self.packet_loss_chance_label, 3, 0, 1, 1)
        self.packet_corruption_chance_slider = QtWidgets.QSlider(self.param_page)
        self.packet_corruption_chance_slider.setProperty("value", 1)
        self.packet_corruption_chance_slider.setOrientation(QtCore.Qt.Horizontal)
        self.packet_corruption_chance_slider.setObjectName("packet_corruption_chance_slider")
        self.param_page_layout.addWidget(self.packet_corruption_chance_slider, 4, 1, 1, 1)
        self.back_button = QtWidgets.QPushButton(self.param_page)
        self.back_button.setObjectName("back_button")
        self.param_page_layout.addWidget(self.back_button, 9, 0, 1, 1)
        self.window_size_value_label = QtWidgets.QLabel(self.param_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.window_size_value_label.sizePolicy().hasHeightForWidth())
        self.window_size_value_label.setSizePolicy(sizePolicy)
        self.window_size_value_label.setMinimumSize(QtCore.QSize(64, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.window_size_value_label.setFont(font)
        self.window_size_value_label.setAlignment(QtCore.Qt.AlignCenter)
        self.window_size_value_label.setObjectName("window_size_value_label")
        self.param_page_layout.addWidget(self.window_size_value_label, 2, 2, 1, 1)
        self.path_line_edit = QtWidgets.QLineEdit(self.param_page)
        self.path_line_edit.setReadOnly(True)
        self.path_line_edit.setObjectName("path_line_edit")
        self.param_page_layout.addWidget(self.path_line_edit, 6, 1, 1, 1)
        self.window_size_label = QtWidgets.QLabel(self.param_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.window_size_label.sizePolicy().hasHeightForWidth())
        self.window_size_label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.window_size_label.setFont(font)
        self.window_size_label.setAlignment(QtCore.Qt.AlignCenter)
        self.window_size_label.setObjectName("window_size_label")
        self.param_page_layout.addWidget(self.window_size_label, 2, 0, 1, 1)
        self.ip_label = QtWidgets.QLabel(self.param_page)
        self.ip_label.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ip_label.sizePolicy().hasHeightForWidth())
        self.ip_label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.ip_label.setFont(font)
        self.ip_label.setAlignment(QtCore.Qt.AlignCenter)
        self.ip_label.setObjectName("ip_label")
        self.param_page_layout.addWidget(self.ip_label, 8, 0, 1, 1)
        self.timeout_label = QtWidgets.QLabel(self.param_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timeout_label.sizePolicy().hasHeightForWidth())
        self.timeout_label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.timeout_label.setFont(font)
        self.timeout_label.setAlignment(QtCore.Qt.AlignCenter)
        self.timeout_label.setObjectName("timeout_label")
        self.param_page_layout.addWidget(self.timeout_label, 5, 0, 1, 1)
        self.packet_corruption_chance_value_label = QtWidgets.QLabel(self.param_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.packet_corruption_chance_value_label.sizePolicy().hasHeightForWidth())
        self.packet_corruption_chance_value_label.setSizePolicy(sizePolicy)
        self.packet_corruption_chance_value_label.setAlignment(QtCore.Qt.AlignCenter)
        self.packet_corruption_chance_value_label.setObjectName("packet_corruption_chance_value_label")
        self.param_page_layout.addWidget(self.packet_corruption_chance_value_label, 4, 2, 1, 1)
        self.packet_size_slider = QtWidgets.QSlider(self.param_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.packet_size_slider.sizePolicy().hasHeightForWidth())
        self.packet_size_slider.setSizePolicy(sizePolicy)
        self.packet_size_slider.setMinimum(1)
        self.packet_size_slider.setMaximum(65507)
        self.packet_size_slider.setSingleStep(1)
        self.packet_size_slider.setPageStep(1024)
        self.packet_size_slider.setProperty("value", 4096)
        self.packet_size_slider.setOrientation(QtCore.Qt.Horizontal)
        self.packet_size_slider.setObjectName("packet_size_slider")
        self.param_page_layout.addWidget(self.packet_size_slider, 0, 1, 1, 1)
        self.packet_loss_chance_slider = QtWidgets.QSlider(self.param_page)
        self.packet_loss_chance_slider.setProperty("value", 5)
        self.packet_loss_chance_slider.setOrientation(QtCore.Qt.Horizontal)
        self.packet_loss_chance_slider.setObjectName("packet_loss_chance_slider")
        self.param_page_layout.addWidget(self.packet_loss_chance_slider, 3, 1, 1, 1)
        self.ip_layout = QtWidgets.QHBoxLayout()
        self.ip_layout.setObjectName("ip_layout")
        self.ip_spin_box_1 = QtWidgets.QSpinBox(self.param_page)
        self.ip_spin_box_1.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ip_spin_box_1.sizePolicy().hasHeightForWidth())
        self.ip_spin_box_1.setSizePolicy(sizePolicy)
        self.ip_spin_box_1.setMaximum(255)
        self.ip_spin_box_1.setProperty("value", 127)
        self.ip_spin_box_1.setObjectName("ip_spin_box_1")
        self.ip_layout.addWidget(self.ip_spin_box_1)
        self.dot_label_1 = QtWidgets.QLabel(self.param_page)
        self.dot_label_1.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dot_label_1.sizePolicy().hasHeightForWidth())
        self.dot_label_1.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(28)
        self.dot_label_1.setFont(font)
        self.dot_label_1.setAlignment(QtCore.Qt.AlignCenter)
        self.dot_label_1.setObjectName("dot_label_1")
        self.ip_layout.addWidget(self.dot_label_1)
        self.ip_spin_box_2 = QtWidgets.QSpinBox(self.param_page)
        self.ip_spin_box_2.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ip_spin_box_2.sizePolicy().hasHeightForWidth())
        self.ip_spin_box_2.setSizePolicy(sizePolicy)
        self.ip_spin_box_2.setMaximum(255)
        self.ip_spin_box_2.setObjectName("ip_spin_box_2")
        self.ip_layout.addWidget(self.ip_spin_box_2)
        self.dot_label_2 = QtWidgets.QLabel(self.param_page)
        self.dot_label_2.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dot_label_2.sizePolicy().hasHeightForWidth())
        self.dot_label_2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(28)
        self.dot_label_2.setFont(font)
        self.dot_label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.dot_label_2.setObjectName("dot_label_2")
        self.ip_layout.addWidget(self.dot_label_2)
        self.ip_spin_box_3 = QtWidgets.QSpinBox(self.param_page)
        self.ip_spin_box_3.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ip_spin_box_3.sizePolicy().hasHeightForWidth())
        self.ip_spin_box_3.setSizePolicy(sizePolicy)
        self.ip_spin_box_3.setMaximum(255)
        self.ip_spin_box_3.setObjectName("ip_spin_box_3")
        self.ip_layout.addWidget(self.ip_spin_box_3)
        self.dot_label_3 = QtWidgets.QLabel(self.param_page)
        self.dot_label_3.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dot_label_3.sizePolicy().hasHeightForWidth())
        self.dot_label_3.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(28)
        self.dot_label_3.setFont(font)
        self.dot_label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.dot_label_3.setObjectName("dot_label_3")
        self.ip_layout.addWidget(self.dot_label_3)
        self.ip_spin_box_4 = QtWidgets.QSpinBox(self.param_page)
        self.ip_spin_box_4.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ip_spin_box_4.sizePolicy().hasHeightForWidth())
        self.ip_spin_box_4.setSizePolicy(sizePolicy)
        self.ip_spin_box_4.setMaximum(255)
        self.ip_spin_box_4.setProperty("value", 1)
        self.ip_spin_box_4.setObjectName("ip_spin_box_4")
        self.ip_layout.addWidget(self.ip_spin_box_4)
        self.param_page_layout.addLayout(self.ip_layout, 8, 1, 1, 1)
        self.gridLayout_3.addLayout(self.param_page_layout, 0, 0, 1, 1)
        self.stacked_widget.addWidget(self.param_page)
        self.log_page = QtWidgets.QWidget()
        self.log_page.setObjectName("log_page")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.log_page)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.stop_button = QtWidgets.QPushButton(self.log_page)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.stop_button.setFont(font)
        self.stop_button.setObjectName("stop_button")
        self.gridLayout_5.addWidget(self.stop_button, 1, 0, 1, 1)
        self.log_text_edit = QtWidgets.QTextEdit(self.log_page)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.log_text_edit.setFont(font)
        self.log_text_edit.setObjectName("log_text_edit")
        self.gridLayout_5.addWidget(self.log_text_edit, 0, 0, 1, 1)
        self.stacked_widget.addWidget(self.log_page)
        self.gridLayout.addWidget(self.stacked_widget, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.central_widget)

        self.retranslateUi(MainWindow)
        self.stacked_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.receiver_button.setText(_translate("MainWindow", "Receiver"))
        self.sender_button.setText(_translate("MainWindow", "Sender"))
        self.timeout_value_label.setText(_translate("MainWindow", "500"))
        self.start_button.setText(_translate("MainWindow", "Start"))
        self.packet_loss_chance_value_label.setText(_translate("MainWindow", "5"))
        self.packet_size_value_label.setText(_translate("MainWindow", "4096"))
        self.packet_size_label.setText(_translate("MainWindow", "Packet Size (B)"))
        self.packet_corruption_chance_label.setText(_translate("MainWindow", "Packet Corruption Chance (%)"))
        self.packet_loss_chance_label.setText(_translate("MainWindow", "Packet Loss Chance (%)"))
        self.back_button.setText(_translate("MainWindow", "Back"))
        self.window_size_value_label.setText(_translate("MainWindow", "32"))
        self.window_size_label.setText(_translate("MainWindow", "Window Size (Packets)"))
        self.ip_label.setText(_translate("MainWindow", "Sender IP"))
        self.timeout_label.setText(_translate("MainWindow", "Timeout (ms)"))
        self.packet_corruption_chance_value_label.setText(_translate("MainWindow", "1"))
        self.dot_label_1.setText(_translate("MainWindow", "."))
        self.dot_label_2.setText(_translate("MainWindow", "."))
        self.dot_label_3.setText(_translate("MainWindow", "."))
        self.stop_button.setText(_translate("MainWindow", "Stop"))
import resources_rc
