import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.uic import loadUi

from Front.form import Ui_MainWindow

from pydispatch import dispatcher

from Receiver import Receiver
from Sender import Sender

SEP = os.path.sep

def createSignal():
    return object()

class MainWindow(QMainWindow):
    SENDER_MODE = 0
    RECEIVER_MODE = 1
    MODE_PAGE = 0
    PARAMETERS_PAGE = 1
    LOG_PAGE = 2

    COLOR_DICT = {
        'SET' : '#C7EA46', # END OF TRANSMISSION (LIME GREEN)
        'SNT' : '#000000', # SENT (BLACK)
        'RCV' : '#1E90FF', # RECEIVED (LIGHT BLUE)
        'ERR' : '#FF0000', # ERROR (RED)
        'WRN' : '#994D00' # WARNING (ORANGE)
    }

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        loadUi("Front/form.ui", self)

        self.clientMode = MainWindow.SENDER_MODE
        self.connectButtons()
        self.connectSliders()
        self.finish_dialog = QFileDialog(self, 'Open')
        self.configureDialogs()

        self.worker = None

        self.LOG_SIGNAL = createSignal()
        self.FINISH_SIGNAL = createSignal()
        self.STOP_SIGNAL = createSignal()
        self.SIGNALS = [self.LOG_SIGNAL, self.FINISH_SIGNAL, self.STOP_SIGNAL]

    def configureDialogs(self):
        self.finish_dialog.setAcceptMode(QFileDialog.AcceptOpen)

    def connectButtons(self):
        self.sender_button.clicked.connect(self.chooseSender)
        self.receiver_button.clicked.connect(self.chooseReceiver)
        self.back_button.clicked.connect(self.backToMode)
        self.start_button.clicked.connect(self.startTransmission)
        self.stop_button.clicked.connect(self.stopTransmission)
        self.path_button.clicked.connect(self.browse)

    def chooseSender(self):
        self.clientMode = MainWindow.SENDER_MODE

        self.packet_size_label.setEnabled(1)
        self.packet_size_slider.setEnabled(1)
        self.packet_size_value_label.setEnabled(1)
        self.window_size_label.setEnabled(1)
        self.window_size_slider.setEnabled(1)
        self.window_size_value_label.setEnabled(1)
        self.packet_loss_chance_label.setEnabled(1)
        self.packet_loss_chance_slider.setEnabled(1)
        self.packet_loss_chance_value_label.setEnabled(1)
        self.packet_corruption_chance_label.setEnabled(1)
        self.packet_corruption_chance_slider.setEnabled(1)
        self.packet_corruption_chance_value_label.setEnabled(1)
        self.timeout_label.setEnabled(1)
        self.timeout_slider.setEnabled(1)
        self.timeout_value_label.setEnabled(1)

        self.path_label.setText('File name')
        self.path_button.setText('Choose file')

        self.finish_dialog.setFileMode(QFileDialog.ExistingFile)

        self.stacked_widget.setCurrentIndex(MainWindow.PARAMETERS_PAGE)

    def chooseReceiver(self):
        self.clientMode = MainWindow.RECEIVER_MODE

        self.packet_size_label.setEnabled(0)
        self.packet_size_slider.setEnabled(0)
        self.packet_size_value_label.setEnabled(0)
        self.window_size_label.setEnabled(0)
        self.window_size_slider.setEnabled(0)
        self.window_size_value_label.setEnabled(0)
        self.packet_loss_chance_label.setEnabled(0)
        self.packet_loss_chance_slider.setEnabled(0)
        self.packet_loss_chance_value_label.setEnabled(0)
        self.packet_corruption_chance_label.setEnabled(0)
        self.packet_corruption_chance_slider.setEnabled(0)
        self.packet_corruption_chance_value_label.setEnabled(0)
        self.timeout_label.setEnabled(0)
        self.timeout_slider.setEnabled(0)
        self.timeout_value_label.setEnabled(0)

        self.path_label.setText('Folder name')
        self.path_button.setText('Choose folder')

        self.finish_dialog.setFileMode(QFileDialog.Directory)

        self.stacked_widget.setCurrentIndex(MainWindow.PARAMETERS_PAGE)

    def backToMode(self):
        self.stacked_widget.setCurrentIndex(MainWindow.MODE_PAGE)

    def startTransmission(self):
        if self.clientMode == MainWindow.RECEIVER_MODE:
            folderName = self.path_line_edit.text()
            if folderName == '':
                folderName = 'test'
            self.worker = Receiver(folderName, self.SIGNALS)

        if self.clientMode == MainWindow.SENDER_MODE:
            fileName = self.path_line_edit.text()

            parameters = []
            parameters += [self.packet_size_slider.value()]
            parameters += [self.window_size_slider.value()]
            parameters += [self.packet_loss_chance_slider.value()]
            parameters += [self.packet_corruption_chance_slider.value()]
            parameters += [self.timeout_slider.value()]

            self.worker = Sender(fileName, self.SIGNALS) # , parameters)

        dispatcher.connect(self.log, self.LOG_SIGNAL, weak=False)
        dispatcher.connect(self.onFinish, self.FINISH_SIGNAL, weak=False)
        self.worker.start()

        self.stacked_widget.setCurrentIndex(MainWindow.LOG_PAGE)

    def stopTransmission(self):
        dispatcher.send(self.STOP_SIGNAL)
        self.onFinish('KILL')

    def connectSliders(self):
        self.packet_size_slider.valueChanged.connect(self.onPacketSizeChange)
        self.window_size_slider.valueChanged.connect(self.onWindowSizeChange)
        self.packet_loss_chance_slider.valueChanged.connect(self.onPacketLossChanceChange)
        self.packet_corruption_chance_slider.valueChanged.connect(self.onPacketCorruptionChanceChange)
        self.timeout_slider.valueChanged.connect(self.onTimeoutChange)

    def onFinish(self, type):
        if type.upper() == 'NORMAL':
            # TODO dispay finished dialog
            pass

        self.stacked_widget.setCurrentIndex(MainWindow.MODE_PAGE)

    def browse(self):
        if self.finish_dialog.exec() == QFileDialog.Accepted:
            path = self.finish_dialog.selectedFiles()[0]
            self.path_line_edit.setText(path)

    def onPacketSizeChange(self):
        newValue = self.packet_size_slider.value()
        self.packet_size_value_label.setText(str(newValue))

    def onWindowSizeChange(self):
        newValue = self.window_size_slider.value()
        self.window_size_value_label.setText(str(newValue))

    def onPacketLossChanceChange(self):
        newValue = self.packet_loss_chance_slider.value()
        self.packet_loss_chance_value_label.setText(str(newValue))

    def onPacketCorruptionChanceChange(self):
        newValue = self.packet_corruption_chance_slider.value()
        self.packet_corruption_chance_value_label.setText(str(newValue))

    def onTimeoutChange(self):
        newValue = self.timeout_slider.value()
        self.timeout_value_label.setText(str(newValue))

    def log(self, logType, logMessage):
        text = f'<span style="font-size:8pt; font-weight:600; color:{MainWindow.COLOR_DICT[logType]};">{logMessage}</span>'
        self.log_text_edit.append(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
