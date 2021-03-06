import sys
from pydispatch import dispatcher

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QDialog, QDialogButtonBox, QHBoxLayout
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal

from Front.form import Ui_MainWindow
from Receiver import Receiver
from Sender import Sender
from enums.finishtypes import FinishTypes
from enums.logtypes import LogTypes


def create_signal():
    return object()


class MainWindow(QMainWindow):
    SENDER_MODE = 0
    RECEIVER_MODE = 1
    MODE_PAGE = 0
    PARAMETERS_PAGE = 1
    LOG_PAGE = 2

    COLOR_DICT = {
        LogTypes.SET: '#C7EA46',  # LIME GREEN
        LogTypes.SNT: '#000000',  # BLACK
        LogTypes.RCV: '#1E90FF',  # LIGHT BLUE
        LogTypes.ERR: '#FF0000',  # RED
        LogTypes.WRN: '#994D00',  # ORANGE
        LogTypes.INF: '#013220',  # DARK GREEN
        LogTypes.OTH: '#871F78'  # DARK PURPLE
    }

    log_signal = pyqtSignal(LogTypes, str)
    on_finish_signal = pyqtSignal(FinishTypes)

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        loadUi("Front/form.ui", self)

        self.client_mode = MainWindow.SENDER_MODE
        self.connect_buttons()
        self.connect_sliders()
        self.path_dialog = QFileDialog(self, 'Open')
        self.finish_dialog = QDialog(self)
        self.configure_dialogs()
        self.init_signals()
        self.connect_signals()

        self.worker = None

    def init_signals(self):
        self.LOG_SIGNAL = create_signal()
        self.FINISH_SIGNAL = create_signal()
        self.SIGNALS = [self.LOG_SIGNAL, self.FINISH_SIGNAL]

    def configure_dialogs(self):
        self.path_dialog.setAcceptMode(QFileDialog.AcceptOpen)

        self.finish_dialog.resize(250, 100)
        button_box = QDialogButtonBox(self.finish_dialog)
        horizontal_layout = QHBoxLayout(self.finish_dialog)
        button_box.setStandardButtons(QDialogButtonBox.Ok)
        button_box.setObjectName("button_box")
        horizontal_layout.addWidget(button_box)
        button_box.accepted.connect(self.finish_dialog.accept)

    def connect_buttons(self):
        self.sender_button.clicked.connect(self.choose_sender)
        self.receiver_button.clicked.connect(self.choose_receiver)
        self.back_button.clicked.connect(self.back_to_mode)
        self.start_button.clicked.connect(self.start_transmission)
        self.stop_button.clicked.connect(self.stop_transmission)
        self.path_button.clicked.connect(self.browse)
        self.back_button_2.clicked.connect(self.back_to_mode)

    def connect_signals(self):
        self.log_signal.connect(self.log)
        self.on_finish_signal.connect(self.on_finish)
        dispatcher.connect(self.trigger_log_signal, self.LOG_SIGNAL, weak=False)
        dispatcher.connect(self.trigger_on_finish_signal, self.FINISH_SIGNAL, weak=False)

    def labelsAndSlidersSetEnabled(self, enabled):
        self.packet_size_label.setEnabled(enabled)
        self.packet_size_slider.setEnabled(enabled)
        self.packet_size_value_label.setEnabled(enabled)
        self.window_size_label.setEnabled(enabled)
        self.window_size_slider.setEnabled(enabled)
        self.window_size_value_label.setEnabled(enabled)
        self.packet_loss_chance_label.setEnabled(enabled)
        self.packet_loss_chance_slider.setEnabled(enabled)
        self.packet_loss_chance_value_label.setEnabled(enabled)
        self.packet_corruption_chance_label.setEnabled(enabled)
        self.packet_corruption_chance_slider.setEnabled(enabled)
        self.packet_corruption_chance_value_label.setEnabled(enabled)
        self.timeout_label.setEnabled(enabled)
        self.timeout_slider.setEnabled(enabled)
        self.timeout_value_label.setEnabled(enabled)
        self.ip_label.setEnabled(not enabled)
        self.dot_label_1.setEnabled(not enabled)
        self.dot_label_2.setEnabled(not enabled)
        self.dot_label_3.setEnabled(not enabled)
        self.ip_spin_box_1.setEnabled(not enabled)
        self.ip_spin_box_2.setEnabled(not enabled)
        self.ip_spin_box_3.setEnabled(not enabled)
        self.ip_spin_box_4.setEnabled(not enabled)

    def choose_sender(self):
        self.client_mode = MainWindow.SENDER_MODE
        self.labelsAndSlidersSetEnabled(1)

        self.path_label.setText('File name')
        self.path_line_edit.setText('')
        self.path_button.setText('Choose file')

        self.path_dialog.setFileMode(QFileDialog.ExistingFile)
        self.stacked_widget.setCurrentIndex(MainWindow.PARAMETERS_PAGE)

    def choose_receiver(self):
        self.client_mode = MainWindow.RECEIVER_MODE
        self.labelsAndSlidersSetEnabled(0)

        self.path_label.setText('Folder name')
        self.path_line_edit.setText('')
        self.path_button.setText('Choose folder')

        self.path_dialog.setFileMode(QFileDialog.Directory)
        self.stacked_widget.setCurrentIndex(MainWindow.PARAMETERS_PAGE)

    def back_to_mode(self):
        self.stacked_widget.setCurrentIndex(MainWindow.MODE_PAGE)

    def getParameters(self):
        parameters = []
        parameters += [self.packet_size_slider.value()]
        parameters += [self.window_size_slider.value()]
        # packet_loss_chance is in % * 10
        parameters += [self.packet_loss_chance_slider.value()]
        # packet_corruption_chance is in % * 10
        parameters += [self.packet_corruption_chance_slider.value()]
        # timeout is in seconds
        parameters += [self.timeout_slider.value() / 1000]
        return parameters

    def start_transmission(self):
        self.stop_button.setEnabled(True)
        self.back_button_2.setEnabled(False)
        self.log_text_edit.clear()

        if self.client_mode == MainWindow.RECEIVER_MODE:
            foldername = self.path_line_edit.text()
            if foldername == '':
                foldername = '.'

            sender_ip = str(self.ip_spin_box_1.value()) + '.' + \
                        str(self.ip_spin_box_2.value()) + '.' + \
                        str(self.ip_spin_box_3.value()) + '.' + \
                        str(self.ip_spin_box_4.value())
            self.worker = Receiver(foldername, sender_ip, self.SIGNALS)

        if self.client_mode == MainWindow.SENDER_MODE:
            filename = self.path_line_edit.text()
            parameters = self.getParameters()
            self.worker = Sender(filename, parameters, self.SIGNALS)

        self.worker.start()
        self.stacked_widget.setCurrentIndex(MainWindow.LOG_PAGE)

    def stop_transmission(self):
        self.worker.terminate()
        self.worker.join()
        self.on_finish(FinishTypes.FORCED)

    def connect_sliders(self):
        self.packet_size_slider.valueChanged.connect(self.on_packet_size_change)
        self.window_size_slider.valueChanged.connect(self.on_window_size_change)
        self.packet_loss_chance_slider.valueChanged.connect(self.on_packet_loss_chance_change)
        self.packet_corruption_chance_slider.valueChanged.connect(self.on_packet_corruption_chance_change)
        self.timeout_slider.valueChanged.connect(self.on_timeout_change)

    def trigger_on_finish_signal(self, type):
        self.on_finish_signal.emit(type)

    def on_finish(self, type, error=''):
        if type == FinishTypes.NORMAL:
            self.finish_dialog.setWindowTitle('Finished')
        elif type == FinishTypes.ERROR:
            self.finish_dialog.setWindowTitle('Error')
        elif type == FinishTypes.FORCED:
            self.finish_dialog.setWindowTitle('Stopped')

        self.finish_dialog.exec()
        self.stop_button.setEnabled(False)
        self.back_button_2.setEnabled(True)

    def browse(self):
        if self.path_dialog.exec() == QFileDialog.Accepted:
            # Single file transmission (get the first selected)
            path = self.path_dialog.selectedFiles()[0]
            self.path_line_edit.setText(path)

    def on_packet_size_change(self):
        newValue = self.packet_size_slider.value()
        self.packet_size_value_label.setText(str(newValue))

    def on_window_size_change(self):
        newValue = self.window_size_slider.value()
        self.window_size_value_label.setText(str(newValue))

    def on_packet_loss_chance_change(self):
        newValue = self.packet_loss_chance_slider.value()
        self.packet_loss_chance_value_label.setText(str(newValue / 10))

    def on_packet_corruption_chance_change(self):
        newValue = self.packet_corruption_chance_slider.value()
        self.packet_corruption_chance_value_label.setText(str(newValue / 10))

    def on_timeout_change(self):
        newValue = self.timeout_slider.value()
        self.timeout_value_label.setText(str(newValue))

    def trigger_log_signal(self, log_type, log_message):
        self.log_signal.emit(log_type, log_message)

    def log(self, log_type, log_message):
        text = f'<span style="font-size:8pt; font-weight:600; color:{MainWindow.COLOR_DICT[log_type]};">{log_message}</span>'
        self.log_text_edit.append(text)


if __name__ == "__main__":
    if len(sys.argv) > 1:  # console mode
        # TODO Silviu daca e sender -> run sender,
        #  receiver -> run receiver
        # handle defaults here!
        # command line params example:
        # 1. path to the file to be sent
        # 2. Receiver address; default (localhost, 8080)
        # 3. Packet size; default 4096 bytes
        # 4. Window size; default 32
        # 5. Timeout interval; default 0.5 sec
        pass

    else:
        app = QApplication(sys.argv)

        window = MainWindow()
        window.show()

        app.exec_()
