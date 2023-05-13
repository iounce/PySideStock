# -*- coding: utf-8 -*-

import os
import time
import datetime
import wcwidth

from PySide6.QtGui import QColor

from language import Language
from theme import Theme

# helper
class StringUtils:
    @staticmethod
    def contains(string, substring):
        return string.find(substring) != -1

class FileUtils:
    @staticmethod
    def get_name(filename):
        return os.path.splitext(filename)[0]

    @staticmethod
    def get_fullname(name, ext = '.xml'):
        if ext in name:
            return name
        return name + ext

class DateUtils:
    @staticmethod
    def get_year():
        return time.strftime('%Y', time.localtime(time.time()))

    @staticmethod
    def get_date():
        return time.strftime('%Y-%m-%d',time.localtime(time.time()))

class ColorUtils:
    @staticmethod
    def hex2rgb(color):
        value = int(color[1:], 16)
        rgb_color = QColor(value)
        rgb_color = QColor(rgb_color.red(), rgb_color.green(), rgb_color.blue())
        return rgb_color.rgb()

class LanguageUtils:
    @staticmethod
    def validate(language):
        languages = [Language.Chinese.value, Language.English.value]
        return language in languages

class ThemeUtils:
    @staticmethod
    def validate(theme):
        theme = FileUtils.get_fullname(theme)
        return theme in Theme.get_all_themes()
    
class UnitHelper():
    balance_unit = 100000000
    balance_unit_text = '亿'

    north_unit = 10000
    north_unit_text = '亿'

class FieldHelper():
    field_date = '日期'
    field_code = '代码'
    field_name = '名称'
    field_open = '今开'
    field_open2 = '开盘'
    field_close = '收盘'
    field_yclose = '昨收'
    field_latest = '最新价'
    field_high = '最高'
    field_low = '最低'
    field_balance = '成交额'
    field_volume = '成交量'
    field_delta = '涨跌幅'
    field_north_sh = '沪股通'
    field_north_sz = '深股通'
    field_value = 'value'
    field_index_list = ['上证指数', '深证成指', '创业板指']

class ColumnHelper():
    index_col_names = ['名称', '最新价', '涨跌幅', '成交额', '沪股通', '深股通']
    table_col_names = ['代码', '名称', '最新价', '涨跌幅', '今开', '昨收', '最高', '最低', '成交额']

class MenuHelper():
    menu_refresh = '刷新'
    menu_copy = '复制'
    
class StockHelper():
    def get_date(sep='-'):
        format = '%Y{0}%m{1}%d'.format(sep, sep)
        return time.strftime(format, time.localtime())

    def get_index_key(index_name, field_name):
        return index_name + '_' + field_name

    def get_common_color(latest_price, yclose_price):
        STANDARD = 0.000001

        value = latest_price - yclose_price

        style = 'color: white'
        if value > STANDARD:
            style = 'color: red'
        elif value < -STANDARD:
            style = 'color: green'

        return style

    def get_field_color(data):
        STANDARD = 0.000001

        data = data.replace(UnitHelper.balance_unit_text, '')
        data = data.replace(UnitHelper.north_unit_text, '')

        try:
            value = float(data)
        except Exception:
            value = 0

        style = 'color: white'
        if value > STANDARD:
            style = 'color: red'
        elif value < -STANDARD:
            style = 'color: green'

        return style

    def format_text(text, width=10):
        count = wcwidth.wcswidth(text) - len(text)
        width = width - count if width >= count else 0
        fill = ''
        return '{0:{1}{2}{3}}'.format(text, fill, '^', width)

    def get_start_date():
        now = datetime.datetime.now()
        date = str(now.year) + '0101'
        return date

    def get_end_date():
        return time.strftime('%Y%m%d', time.localtime())
