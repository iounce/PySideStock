# -*- coding: utf-8 -*-

import pandas as pd
import akshare as ak
import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QDialog, QWidget, QLabel, QPushButton, QSpacerItem, QGridLayout, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, QSize
from icon import LogoIcon, MenuIcon
from style import ButtonStyle, WidgetStyle
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


class KLineWidget(QDialog):
    def __init__(self, parent, stock_code, start_date, end_date):
        super().__init__(parent)
        
        self.init_base_layout()
        self.init_menu(stock_code)
        self.init_kline(stock_code, start_date, end_date)

        self.resize(900, 540)
        
    def init_base_layout(self):
        self.grid = QGridLayout(self)
        
        self.layout_head = QHBoxLayout()
        self.layout_body= QHBoxLayout()
        self.grid.addLayout(self.layout_head, 0, 0, 1, 2)
        self.grid.addLayout(self.layout_body, 1, 0, 1, 2)
        
        self.setObjectName('wid_main')
        self.setStyleSheet(WidgetStyle.get_border('wid_main'))
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
    def init_menu(self, stock_code):
        lbl_logo = QLabel(self)
        lbl_logo.setEnabled(True)
        lbl_logo.setMinimumSize(QSize(24, 24))
        lbl_logo.setMaximumSize(QSize(24, 24))
        lbl_logo.setPixmap(LogoIcon.get_pixmap())
        lbl_logo.setScaledContents(True)
        
        lbl_blank = QLabel(self)
        lbl_blank.setFixedWidth(4)
        
        lbl_title = QLabel(self)
        lbl_title.setMinimumSize(QSize(80, 32))
        lbl_title.setMaximumSize(QSize(80, 32))
        lbl_title.setText(stock_code)
        
        spacer = QSpacerItem(32, 32, QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        btn_close = QPushButton(self)
        btn_close.setMinimumSize(QSize(32, 32))
        btn_close.setMaximumSize(QSize(32, 32))
        btn_close.setFlat(True)
        btn_close.setIcon(MenuIcon.get_close())
        btn_close.setIconSize(QSize(24, 24))
        btn_close.setText('')
        btn_close.setStyleSheet(ButtonStyle.get_close())
        btn_close.clicked.connect(self.on_exit)
        
        self.layout_head.setSpacing(2)
        self.layout_head.addWidget(lbl_logo)
        self.layout_head.addWidget(lbl_blank)
        self.layout_head.addWidget(lbl_title)
        self.layout_head.addItem(spacer)
        self.layout_head.addWidget(btn_close)
    
    def init_kline(self, stock_code, start_date, end_date):
        kline = KLine(stock_code, start_date, end_date)
        widget = kline.draw()
        if not widget:
            widget = QWidget()
            
        self.layout_body.addWidget(widget)
    
    def on_exit(self):
        self.close()
        
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.is_moving = True
            self.start_point = e.globalPosition().toPoint()
            self.window_point = self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self.is_moving:
            pos = e.globalPosition().toPoint() - self.start_point
            self.move(self.window_point + pos)

    def mouseReleaseEvent(self, e):
        self.is_moving = False
