class Logger:

    def __init__(self, logger, alert_function, alert_settings):
        self.logger = logger

        self.alert_function = alert_function
        self.alert_settings = alert_settings

    def error(self, message, alert=True):
        self.logger.error(message)
        if alert: self.alert_function(message, **self.alert_settings)

    def warning(self, message, alert=False):
        self.logger.warning(message)
        if alert: self.alert_function(message, 'WARNING', **self.alert_settings)

    def info(self, message, alert=False):
        self.logger.info(message)
        if alert: self.alert_function(message, 'INFO', **self.alert_settings)

    def debug(self, message, alert=False):
        self.logger.debug(message)
        if alert: self.alert_function(message, 'DEBUG', **self.alert_settings)
