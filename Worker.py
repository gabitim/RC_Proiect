class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    file_sent = pyqtSignal(str)
    feedback_received = pyqtSignal()
    modify_status = pyqtSignal()
    recording_saved = pyqtSignal([list])
    dummy_recording_saved = pyqtSignal([list])
    # recording_saved_second_callback = pyqtSignal([list])


class Worker(QRunnable):
    def __init__(self, given_task, *args, **kwargs):
        super(Worker, self).__init__()
        self.task = given_task
        self.args = args
        self.kwargs = kwargs
        # self.signals = WorkerSignals()
        # self.kwargs['recording_dummy_saved_callback'] = self.signals.dummy_recording_saved
        # self.kwargs['recording_saved_callback'] = self.signals.recording_saved
        # self.kwargs['file_sent_callback'] = self.signals.file_sent
        # self.kwargs['feedback_received_callback'] = self.signals.feedback_received
        # self.kwargs['modify_status_callback'] = self.signals.modify_status
        # self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        try:
            result = self.task(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            # self.signals.error.emit((exctype, value, traceback.format_exc()))
        # else:
            # self.signals.result.emit(result)  # Return the result of the processing
        # finally:
            # self.signals.finished.emit()  # Done

    def send_notificaton(self, *args):
        self.console_text += ("\n<CAR-COV :> " + args[0])

        if len(self.console_text) > 400:
            self.console_text = ""
            # self.consoleWindow.clear() # triggers exception at thread contect swap

        self.consoleWindow.insertPlainText("\n<CAR-COV :> " + args[0])
