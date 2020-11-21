import sys
from pydispatch import dispatcher

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal

from Front.form import Ui_MainWindow
from Receiver import Receiver
from Sender import Sender
from Components.Logger import 


def create_signal():
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
        'WRN' : '#994D00', # WARNING (ORANGE)
        'INF' : '#013220'  # INFORMATIVE (DARK GREEN)
    }

    log_signal = pyqtSignal(str, str)
    on_finish_signal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        loadUi("Front/form.ui", self)

        self.client_mode = MainWindow.SENDER_MODE
        self.connect_buttons()
        self.connect_sliders()
        self.finish_dialog = QFileDialog(self, 'Open')
        self.configure_dialogs()
        self.init_signals()

        self.worker = None

    def init_signals(self):
        self.LOG_SIGNAL = create_signal()
        self.FINISH_SIGNAL = create_signal()
        self.STOP_SIGNAL = create_signal()
        self.SIGNALS = [self.LOG_SIGNAL, self.FINISH_SIGNAL, self.STOP_SIGNAL]

    def configure_dialogs(self):
        self.finish_dialog.setAcceptMode(QFileDialog.AcceptOpen)

    def connect_buttons(self):
        self.sender_button.clicked.connect(self.choose_sender)
        self.receiver_button.clicked.connect(self.choose_receiver)
        self.back_button.clicked.connect(self.back_to_mode)
        self.start_button.clicked.connect(self.start_transmission)
        self.stop_button.clicked.connect(self.stop_transmission)
        self.path_button.clicked.connect(self.browse)

    def choose_sender(self):
        self.client_mode = MainWindow.SENDER_MODE

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

    def choose_receiver(self):
        self.client_mode = MainWindow.RECEIVER_MODE

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

    def back_to_mode(self):
        self.stacked_widget.setCurrentIndex(MainWindow.MODE_PAGE)

    def parameters(self):
        parameters = []
        parameters += [self.packet_size_slider.value()]
        parameters += [self.window_size_slider.value()]
        parameters += [self.packet_loss_chance_slider.value()]
        parameters += [self.packet_corruption_chance_slider.value()]
        parameters += [self.timeout_slider.value()]
        return parameters

    def start_transmission(self):
        if self.client_mode == MainWindow.RECEIVER_MODE:
            foldername = self.path_line_edit.text()
            if foldername == '':
                foldername = '.'

            self.worker = Receiver(foldername, self.SIGNALS)

        if self.client_mode == MainWindow.SENDER_MODE:
            filename = self.path_line_edit.text()

            parameters = self.parameters()

            self.worker = Sender(filename, self.SIGNALS) # , parameters)

        self.log_signal.connect(self.log)
        self.on_finish_signal.connect(self.on_finish)
        dispatcher.connect(self.trigger_log_signal, self.LOG_SIGNAL, weak=False)
        dispatcher.connect(self.trigger_on_finish_signal, self.FINISH_SIGNAL, weak=False)
        self.worker.start()

        self.stacked_widget.setCurrentIndex(MainWindow.LOG_PAGE)

    def stop_transmission(self):
        dispatcher.send(self.STOP_SIGNAL)
        self.on_finish('KILL')

    def connect_sliders(self):
        self.packet_size_slider.valueChanged.connect(self.on_packet_size_change)
        self.window_size_slider.valueChanged.connect(self.on_window_size_change)
        self.packet_loss_chance_slider.valueChanged.connect(self.on_packet_loss_chance_change)
        self.packet_corruption_chance_slider.valueChanged.connect(self.on_packet_corruption_chance_change)
        self.timeout_slider.valueChanged.connect(self.on_timeout_change)

    def trigger_on_finish_signal(self, type):
        self.on_finish_signal.emit(type)

    def on_finish(self, type):
        if type.upper() == 'NORMAL':
            # TODO dispay finished dialog
            pass

        self.stacked_widget.setCurrentIndex(MainWindow.MODE_PAGE)

    def browse(self):
        if self.finish_dialog.exec() == QFileDialog.Accepted:
            path = self.finish_dialog.selectedFiles()[0]
            self.path_line_edit.setText(path)

    def on_packet_size_change(self):
        newValue = self.packet_size_slider.value()
        self.packet_size_value_label.setText(str(newValue))

    def on_window_size_change(self):
        newValue = self.window_size_slider.value()
        self.window_size_value_label.setText(str(newValue))

    def on_packet_loss_chance_change(self):
        newValue = self.packet_loss_chance_slider.value()
        self.packet_loss_chance_value_label.setText(str(newValue))

    def on_packet_corruption_chance_change(self):
        newValue = self.packet_corruption_chance_slider.value()
        self.packet_corruption_chance_value_label.setText(str(newValue))

    def on_timeout_change(self):
        newValue = self.timeout_slider.value()
        self.timeout_value_label.setText(str(newValue))

    def trigger_log_signal(self, log_type, log_message):
        self.log_signal.emit(log_type, log_message)

    def log(self, log_type, log_message):
        text = f'<span style="font-size:8pt; font-weight:600; color:{MainWindow.COLOR_DICT[log_type]};">{log_message}</span>'
        self.log_text_edit.append(text)


if __name__ == "__main__":
    # TODO add if sys.argv > ce trb, launch console app

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
