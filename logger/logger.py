class Logger:

    def __init__(self, logger, alert_function, alert_settings):
        self.logger = logger

        self.alert_function = alert_function
        self.alert_settings = alert_settings

    def error(self, message, alert=True):
        pass

    def warning(self, message, alert=False):
        pass

    def info(self, message, alert=False):
        pass

    def debug(self, message, alert=False):
        pass
