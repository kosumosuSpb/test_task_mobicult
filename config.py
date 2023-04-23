import logging


DATE_FORMAT = '%d.%m.%Y'
DB_NAME = 'db.sqlite'

API = 'http://www.cbr.ru/scripts/XML_daily.asp?date_req='
EUR = 'EUR'
USD = 'USD'


def get_logger(
        name: str,
        level=logging.INFO,
        fmt='%(asctime)s - [%(levelname)s] - %(name)s: %(message)s'
) -> logging.Logger:
    """
    Принимает имя для логгера (также можно установить уровень и формат),
    возвращает объект логгера. Настраивает только для StreamHandler

    :param name: имя для логгера
    :param level: уровень логгера
    :param fmt: формат логгера
    :return: объект логгера
    """
    logger = logging.getLogger(name)
    formatter = logging.Formatter(fmt)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
