import requests
from datetime import datetime
import xml.etree.ElementTree as ET
from typing import Union, Dict, Tuple
#
from config import API, EUR, USD, DATE_FORMAT, get_logger


logger = get_logger(__name__)


def get_value(
        codes: Union[str, list, tuple],
        date: Union[str, datetime, None] = None
) -> Dict[str, Union[Tuple[float, int], str]]:
    """
    По введённым коду валюты и дате выводит словарь со значениями валют в рублях и датой

    :param codes: Строка или список строк с кодами валют
    :param date: дата на которую нужны значения
    :return: словарь вида: {'date' 'ДД.ММ.ГГГГ', 'code1': (00.0000, 1), 'code2': (00.0000, 10), }
                            где в кортеже первый элемент -- это значение в рублях,
                            а второй -- номинал (за сколько единиц валюты)
    """
    if not isinstance(date, (str, datetime, type(None))):
        raise ValueError('Wrong date type! Must be str, datetime or None.')

    date = date or _today_str()
    xml_string = _get_xml_string_from_cbrf(date)

    return _get_valute_value_from_xml(codes, xml_string)


def _get_xml_string_from_cbrf(date: Union[str, datetime], api_url=API) -> str:
    """
    Получает XML с сайта ЦБ РФ

    :param date: дата, на которую нужен курс. Формат даты: ДД/ММ/ГГГГ или ДД.ММ.ГГГГ
    :param api_url: Адрес API
    :return: строка XML
    """
    if isinstance(date, datetime):
        date: str = datetime.strftime(date, DATE_FORMAT)

    try:
        response = requests.get(api_url + date)
    except requests.exceptions.HTTPError as he:
        logger.error(f'Ошибка соединения с API сервером: {he}')
        raise requests.exceptions.HTTPError
    return response.text


def _get_valute_value_from_xml(codes: Union[str, list], xml_string: str) -> dict:
    """Возвращает значение валюты по введённому коду"""
    root = ET.fromstring(xml_string)

    if isinstance(codes, str):
        codes = [codes, ]

    date = root.attrib.get('Date')
    valute_dict = {'date': date}

    for code in codes:
        code = code.upper()
        valute_obj = root.find(f'./Valute/[CharCode="{code}"]')
        value = valute_obj.find('Value').text if valute_obj else 'NotFound'
        nominal = valute_obj.find('Nominal').text if valute_obj else '0'
        valute_dict[code] = (value.replace(',', '.'), int(nominal))

    return valute_dict


def _today_str() -> str:
    """Возвращает текущую дату в строке в формате ДД/ММ/ГГГГ"""
    return datetime.strftime(datetime.today(), DATE_FORMAT)
