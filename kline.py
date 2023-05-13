# -*- coding: utf-8 -*-

import pandas as pd
import akshare as ak
import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6 import QtWidgets
from utils import FieldHelper

class KLine():
    def __init__(self, stock_code, start_date, end_date):
        self.stock_code = stock_code
        self.start_date = start_date
        self.end_date = end_date

    def fetch(self):
        df = ak.stock_zh_a_hist(
            symbol=self.stock_code, start_date=self.start_date, end_date=self.end_date)
        return df

    def draw(self):
        df = self.fetch()
        if df is None or df.empty:
            return None

        df['date'] = df[FieldHelper.field_date]
        df['open'] = df[FieldHelper.field_open2]
        df['high'] = df[FieldHelper.field_high]
        df['low'] = df[FieldHelper.field_low]
        df['close'] = df[FieldHelper.field_close]
        df['volume'] = df[FieldHelper.field_volume] / 10000
        df.index = pd.DatetimeIndex(df['date'])

        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        my_color = mpf.make_marketcolors(
            up='r', down='g', edge='inherit', wick='inherit', volume='inherit')
        my_style = mpf.make_mpf_style(rc={'font.family': 'SimHei'},
                                      marketcolors=my_color,
                                      figcolor='(0.82,0.83,0.85)',
                                      gridcolor='(0.82,0.83,0.85)')

        fig, _ = mpf.plot(
            df, type='candle', mav=(5, 10, 20, 30, 60, 120, 250),
            datetime_format='%Y-%m-%d',
            ylabel='', ylabel_lower='', style=my_style,
            volume=True, tight_layout=True, returnfig=True)

        canvas = FigureCanvas(fig)

        return canvas


class KLineWidget(QtWidgets.QDialog):
    def __init__(self, parent, stock_code, start_date, end_date):
        super().__init__(parent)

        kline = KLine(stock_code, start_date, end_date)
        widget = kline.draw()
        if not widget:
            widget = QtWidgets.QWidget()

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(widget)

        self.resize(900, 540)
