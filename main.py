import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi

from Front.form import Ui_MainWindow

from Receiver import Receiver
from Sender import Sender


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

        self.worker = None

    def connectButtons(self):
        self.senderButton.clicked.connect(self.chooseSender)
        self.receiverButton.clicked.connect(self.chooseReceiver)
        self.backButton.clicked.connect(self.backToMode)
        self.startButton.clicked.connect(self.startTransmission)
        self.stopButton.clicked.connect(self.stopTransmission)

    def chooseSender(self):
        self.clientMode = MainWindow.SENDER_MODE

        self.packetSizeLabel.setEnabled(1)
        self.packetSizeSlider.setEnabled(1)
        self.packetSizeValueLabel.setEnabled(1)
        self.windowSizeLabel.setEnabled(1)
        self.windowSizeSlider.setEnabled(1)
        self.windowSizeValueLabel.setEnabled(1)
        self.packetLossChanceLabel.setEnabled(1)
        self.packetLossChanceSlider.setEnabled(1)
        self.packetLossChanceValueLabel.setEnabled(1)
        self.packetCorruptionChanceLabel.setEnabled(1)
        self.packetCorruptionChanceSlider.setEnabled(1)
        self.packetCorruptionChanceValueLabel.setEnabled(1)
        self.timeoutLabel.setEnabled(1)
        self.timeoutSlider.setEnabled(1)
        self.timeoutValueLabel.setEnabled(1)

        self.stackedWidget.setCurrentIndex(MainWindow.PARAMETERS_PAGE)

    def chooseReceiver(self):
        self.clientMode = MainWindow.RECEIVER_MODE

        self.packetSizeLabel.setEnabled(0)
        self.packetSizeSlider.setEnabled(0)
        self.packetSizeValueLabel.setEnabled(0)
        self.windowSizeLabel.setEnabled(0)
        self.windowSizeSlider.setEnabled(0)
        self.windowSizeValueLabel.setEnabled(0)
        self.packetLossChanceLabel.setEnabled(0)
        self.packetLossChanceSlider.setEnabled(0)
        self.packetLossChanceValueLabel.setEnabled(0)
        self.packetCorruptionChanceLabel.setEnabled(0)
        self.packetCorruptionChanceSlider.setEnabled(0)
        self.packetCorruptionChanceValueLabel.setEnabled(0)
        self.timeoutLabel.setEnabled(0)
        self.timeoutSlider.setEnabled(0)
        self.timeoutValueLabel.setEnabled(0)

        self.stackedWidget.setCurrentIndex(MainWindow.PARAMETERS_PAGE)

    def backToMode(self):
        self.stackedWidget.setCurrentIndex(MainWindow.MODE_PAGE)

    def startTransmission(self):
        # start transmission thread
        if self.clientMode == MainWindow.RECEIVER_MODE:
            folderName = "F:\\Proj\\RC_Proiect\\test\\receive"
            self.worker = Receiver(folderName)

        if self.clientMode == MainWindow.SENDER_MODE:
            fileName = "F:\\Proj\\RC_Proiect\\test\\send\\test.jpg"
            self.worker = Sender(fileName)

        self.worker.log_signal.connect(self.log)
        self.worker.start()

        self.stackedWidget.setCurrentIndex(MainWindow.LOG_PAGE)

    def stopTransmission(self):
        # safely stop transmission thread
        pass

        self.stackedWidget.setCurrentIndex(MainWindow.MODE_PAGE)

    def connectSliders(self):
        self.packetSizeSlider.valueChanged.connect(self.onPacketSizeChange)
        self.windowSizeSlider.valueChanged.connect(self.onWindowSizeChange)
        self.packetLossChanceSlider.valueChanged.connect(self.onPacketLossChanceChange)
        self.packetCorruptionChanceSlider.valueChanged.connect(self.onPacketCorruptionChanceChange)
        self.timeoutSlider.valueChanged.connect(self.onTimeoutChange)

    def onPacketSizeChange(self):
        newValue = self.packetSizeSlider.value()
        self.packetSizeValueLabel.setText(str(newValue))

    def onWindowSizeChange(self):
        newValue = self.windowSizeSlider.value()
        self.windowSizeValueLabel.setText(str(newValue))

    def onPacketLossChanceChange(self):
        newValue = self.packetLossChanceSlider.value()
        self.packetLossChanceValueLabel.setText(str(newValue))

    def onPacketCorruptionChanceChange(self):
        newValue = self.packetCorruptionChanceSlider.value()
        self.packetCorruptionChanceValueLabel.setText(str(newValue))

    def onTimeoutChange(self):
        newValue = self.timeoutSlider.value()
        self.timeoutValueLabel.setText(str(newValue))

    def log(self, logType, logMessage):
        text = f'<span style="font-size:8pt; font-weight:600; color:{MainWindow.COLOR_DICT[logType]};">{logMessage}</span>'
        self.logTextEdit.append(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
