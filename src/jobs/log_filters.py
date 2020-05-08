class LevelFilter():
    log_levels = {
        'CRITICAL': 50,
        'ERROR': 40,
        'WARNING': 30,
        'INFO': 20,
        'DEBUG': 10,
        'NOTSET': 0
    }

    def __init__(self, level):
        self.__level = self.log_levels.get(level)

    def filter(self, logRecord):
        levelno = self.__level
        return logRecord.levelno == levelno
