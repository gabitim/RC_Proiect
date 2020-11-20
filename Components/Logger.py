from pydispatch import dispatcher

class Logger:
    def __init__(self, LOG_SIGNAL=None):
        if LOG_SIGNAL is None:
            self.console_mode = True
        else:
            self.LOG_SIGNAL = LOG_SIGNAL
            self.console_mode = False

    def log(self, log_type, log_message):
        if self.console_mode:
            # TODO Silviu fa log cum vrei tu AICI!
            pass
        else: # QT logging
            dispatcher.send(self.LOG_SIGNAL, log_type=log_type, log_message=log_message)
