import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi

from Front.form import Ui_MainWindow

class MainWindow(QMainWindow):
    SENDER_MODE = 0
    RECEIVER_MODE = 1
    SR_PAGE = 0
    PARAMETERS_PAGE = 1
    LOG_PAGE = 2

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        loadUi("Front/form.ui", self)

        self.clientMode = SENDER_MODE
        self.connectButtons()

    def connectButtons(self):
        self.senderButton.clicked.connect(self.chooseSender)
        self.receiverButton.clicked.connect(self.chooseReceiver)
        self.backButton.clicked.connect(self.backToMode)
        self.startButton.clicked.connect(self.startTransmission)
        self.stopButton.clicked.connect(self.stopTransmission)

    def chooseSender(self):
        self.clientMode = SENDER_MODE

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

        self.stackedWidget.setCurrentIndex(PARAMETERS_PAGE)

    def chooseReceiver(self):
        self.clientMode = RECEIVER_MODE

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

        self.stackedWidget.setCurrentIndex(PARAMETERS_PAGE)

    def backToMode(self):
        pass

    def startTransmission(self):
        pass

    def stopTransmission(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
