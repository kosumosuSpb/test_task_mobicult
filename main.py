from flask import Flask, render_template, request
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from typing import Tuple, Dict, Union
#
from get_values import get_value
from config import EUR, USD, DATE_FORMAT, get_logger
from db_tool import SimpleDB


logger = get_logger(__name__)
app = Flask(__name__, template_folder='templates', static_folder='templates')
db = SimpleDB()

scheduler = BackgroundScheduler()
start_date = datetime.today().replace(hour=10, minute=0, second=0, microsecond=0)
# scheduler.add_job находится внизу


@app.route("/")
def root():
    """Отображает основную страницу с текущим курсом валют"""
    date = datetime.today()
    date, values = _get_currency(date, EUR, USD)

    return render_template('index.html', date=date, values=values)


@app.route('/submit-date/', methods=['POST'])
def submit_date():
    """Забирает данные от формы ввода даты через Flask.request и возвращает результат с курсами на эту дату"""
    date = request.form.get('date')  # Получаем значение поля 'date' из формы. Данные придут в формате ГГГГ-ММ-ДД
    if date:
        date = '.'.join(date.split('-')[::-1])

    date, values = _get_currency(date, EUR, USD)  # придёт кортеж вида ('date': '23.04.2023', {'EUR': (89.3495, 1), })

    return render_template('index.html', date=date, values=values)


# Helping functions

def task_everyday_currency_check():
    """Задача, которая будет проверять курс и записывать данные в БД"""
    logger.info(f"Старт проверки курса валют на дату {datetime.strftime(datetime.today(), DATE_FORMAT)}")
    print(f"Старт проверки курса валют на дату {datetime.strftime(datetime.today(), DATE_FORMAT)}")
    values = get_value([EUR, USD])
    date = values.pop('date')

    for code, val in values.items():
        value, nominal = val
        status = db.set_currency(date, code, value, nominal)  # статус можно использовать для дебага и логгинга


def _get_currency(date: Union[str, datetime], *codes: str) -> Tuple[str, Dict[str, Tuple[float, int]]]:
    currency_list = db.get_currency(date)  # запрашиваем из БД

    codes = codes or (EUR, USD)

    if not currency_list:  # если в БД нет, то получаем новые данные
        values = get_value(codes, date)
        date = values.pop('date')

        for code, val in values.items():
            value, nominal = val
            status = db.set_currency(date, code, value, nominal)
    else:
        # [('23/04/2023', 'USD', 75.5, 1)]
        values = dict()
        for date_curr in currency_list:
            date, code, value, nominal = date_curr
            values[code] = (value, nominal)

    return date, values


scheduler.add_job(task_everyday_currency_check, 'interval', days=1, start_date=start_date, id='get_currency_task')
scheduler.start()

scheduler.print_jobs()
