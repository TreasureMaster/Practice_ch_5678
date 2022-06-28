# Различные функции для парсинга SQL файлов.
import itertools
import json

import sqlparse
from sql_metadata import Parser
from dateutil.parser import parse


def grouper(iterable, n, fillvalue=None):
    """Функция для разделения списка на равные части (предложена в документации (Python)
    
    :param iterable: Итерируемый объект (н-р, список)
    :param n: Количество элементов в отделенных частях на выходе
    :param fillvalue: Заполнитель для отсутствующих элементов
    """
    return itertools.zip_longest(
        *([iter(iterable)]*n),
        fillvalue=fillvalue
    )


def dict_from_lists(headers, values):
    """Создает словарь из списков ключей и значений
    
    :param headers: Ключи создаваемого словаря
    :param values: Список значений словаря
    """
    return [
        {key: value for key, value in zip(ks, vs)}
        for ks, vs in zip(
            itertools.cycle([headers]),
            grouper(values, len(headers))
        )
    ]


def convert_hook(dct):
    """Конвертирует строки JSON ('true', 'false', 'null') и даты в типы Python"""
    _mapper = {
        'true': True,
        'false': False,
        'null': None,
    }
    for key, value in dct.items():
        if isinstance(value, str):
            if (val := value.lower()) in ('true', 'false', 'null'):
                dct[key] = _mapper[val]
            if value.replace('-', '').isdigit():
                try:
                    dt_date = parse(value).date()
                except ValueError:
                    pass
                else:
                    dct[key] = dt_date
    return dct


def get_inserts_from_files(filename):
    """Выделяет из SQL-файла значения для INSERT"""
    all_queries = open(filename, encoding='utf-8').read()

    inserts = {}
    for query in sqlparse.split(all_queries):
        parsed = Parser(sqlparse.format(query, strip_comments=True))
        if parsed.query_type.value == 'INSERT':
            insert_list = dict_from_lists(parsed.columns, parsed.values)
            inserts[parsed.tables[0].split('.')[-1]] = insert_list
    inserts = json.loads(json.dumps(inserts), object_hook=convert_hook)
    return inserts