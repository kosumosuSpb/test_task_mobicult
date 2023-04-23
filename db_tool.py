import sqlite3
from datetime import datetime
from typing import Union, List, Tuple, Optional
#
from config import DATE_FORMAT, DB_NAME, get_logger


logger = get_logger(__name__)


class SimpleDB:
    def __init__(self):
        self.db_name = DB_NAME
        self.create_database()

    def set_currency(
            self,
            date: Union[str, datetime],
            currency_name: str,
            currency_value: Union[str, float],
            currency_nominal: Union[str, int]
    ) -> bool or None:
        """Запись курса валюты на конкретную дату"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        if isinstance(date, datetime):
            date = datetime.strftime(date, DATE_FORMAT)

        try:
            c.execute('INSERT INTO currency (date, name, value, nominal) VALUES (?, ?, ?, ?)',
                      (date, currency_name, currency_value, currency_nominal))
            conn.commit()
            logger.info(f"Запись для {date} - {currency_name} создана.")
            return True
        except sqlite3.IntegrityError:
            logger.debug(f"Запись для {date} уже существует в БД.")
        except Exception as e:
            logger.error(f"Ошибка при создании записи в БД: {e}")
        finally:
            conn.close()

    def get_currency(
            self,
            date: Union[str, datetime],
            currency_name: Optional[str] = None
    ) -> List[Tuple[str, str, float, int]]:
        """
        Чтение курса валюты на конкретную дату

        :param date: Дата в str или datetime формате. Если это строка, то ДД/ММ/ГГГГ или ДД.ММ.ГГГГ
        :param currency_name: имя (код) валюты
        :return: список кортежей: [('23/04/2023', 'USD', 75.5, 1), ].
                    Если указан код валюты, то кортеж будет один, а если только дата, то вернутся все валюты на эту даты
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        if isinstance(date, datetime):
            date = datetime.strftime(date, DATE_FORMAT)

        if currency_name:
            c.execute('SELECT * FROM currency WHERE date = ? AND name = ?', (date, currency_name))
        else:
            c.execute('SELECT * FROM currency WHERE date = ?', (date, ))
        data = c.fetchall()
        conn.close()
        return data

    def create_database(self):
        """Создание таблицы в БД с нужными полями для данного приложения"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE if not exists currency 
                    (date TEXT, name TEXT, value REAL, nominal INTEGER, 
                    PRIMARY KEY (date, name))''')
        conn.commit()
        conn.close()
        logger.info("БД создана или уже существовала")
