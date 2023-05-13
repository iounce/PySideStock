# -*- coding: utf-8 -*-

import enum
from kline import KLineWidget
from utils import ColumnHelper, MenuHelper, UnitHelper, FieldHelper, StockHelper
import akshare as ak
import pandas as pd
from PySide6.QtGui import QGuiApplication, QCursor
from PySide6.QtWidgets import QWidget, QMenu, QLabel, QGridLayout, QHBoxLayout, QVBoxLayout, QTableWidget, QAbstractItemView, QHeaderView
from PySide6.QtCore import Qt

class StockMarket(enum.Enum):
    SH = 1
    SZ = 2
    
class StockInfo():
    def __init__(self, index_list, stock_list):
        self.index_list = index_list
        self.stock_list = stock_list

    def fetch_index_all(self):
        df = ak.stock_zh_index_spot()
        df = self.filter_index(df)

        df[FieldHelper.field_balance] = df[FieldHelper.field_balance].apply(
            lambda x: format(x / UnitHelper.balance_unit,
                             '.2f') + UnitHelper.balance_unit_text
        )

        return df

    def fetch_north(self, type):
        df = None
        if type == StockMarket.SH:
            df = ak.stock_hsgt_north_net_flow_in_em(
                symbol=FieldHelper.field_north_sh)
            df = self.filter_north(df)
        elif type == StockMarket.SZ:
            df = ak.stock_hsgt_north_net_flow_in_em(
                symbol=FieldHelper.field_north_sz)
            df = self.filter_north(df)

        return df

    def fetch_stock(self, type):
        df = None
        if type == StockMarket.SH:
            df = ak.stock_sh_a_spot_em()
        elif type == StockMarket.SZ:
            df = ak.stock_sz_a_spot_em()
        return self.filter_stock(df)

    def fetch_stock_all(self):
        df_sh = self.fetch_stock(StockMarket.SH)
        df_sz = self.fetch_stock(StockMarket.SZ)
        df = pd.concat([df_sh, df_sz])
        df[FieldHelper.field_balance] = df[FieldHelper.field_balance].apply(
            lambda x: format(x / UnitHelper.balance_unit,
                             '.2f') + UnitHelper.balance_unit_text
        )

        return df.reset_index(drop=True)

    def filter_index(self, df):
        return self.filter(df, self.index_list)

    def filter_north(self, df):
        cond = "date == " + "'" + StockHelper.get_date() + "'"
        df = df.query(cond)
        df[FieldHelper.field_value] = df[FieldHelper.field_value].apply(
            lambda x: format(x / UnitHelper.north_unit, '.2f') +
            UnitHelper.north_unit_text
        )
        return df.reset_index(drop=True)

    def filter_stock(self, df):
        return self.filter(df, self.stock_list)

    def filter(self, df, data):
        expr = ''
        i = 0
        for cond in data:
            if i == len(data) - 1:
                expr += "(" + FieldHelper.field_name + \
                    " == " + '"' + cond + '"' + ")"
            else:
                expr += "(" + FieldHelper.field_name + " == " + \
                    '"' + cond + '"' + ")" " or "

            i += 1

        df = df.query(expr)
        return df.reset_index(drop=True)

class StockWidget(QWidget):
    def __init__(self, stock_list):
        super().__init__()

        self.clipboard = QGuiApplication.clipboard()
        
        self.index_list = FieldHelper.field_index_list
        self.stock_info = StockInfo(self.index_list, stock_list)

        self.init_base_layout()

        self.init_context_menu()

        self.init_stock_layout()
        self.init_index_layout()

        df = self.fetch_stock()
        self.update_stock_info(df)

        df = self.fetch_index()
        self.update_index_info(df)

    def init_context_menu(self):
        self.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        self.context_menu = QMenu(self)
        self.action_refresh = self.context_menu.addAction(
            MenuHelper.menu_refresh)
        self.action_refresh.triggered.connect(self.do_action_refresh)

        self.action_copy = self.context_menu.addAction(MenuHelper.menu_copy)
        self.action_copy.triggered.connect(self.do_action_copy)

    def showContextMenu(self):
        self.context_menu.move(QCursor().pos())
        self.context_menu.show()

    def do_action_refresh(self):
        df = self.fetch_stock()
        self.update_stock_info(df)

        df = self.fetch_index()
        self.update_index_info(df)

    def do_action_copy(self):
        row_count = self.table.rowCount()
        column_count = self.table.columnCount()

        content = ''

        index = 0
        for name in ColumnHelper.table_col_names:
            name = StockHelper.format_text(name)
            content += name

            index += 1
        content += '\n'

        for row in range(row_count):
            index = 0
            for column in range(column_count):
                item = self.table.cellWidget(row, column)

                text = item.text()
                text = StockHelper.format_text(text)
                content += text

                index += 1
            content += '\n'

        print(content)
        self.clipboard.setText(content)

    def init_base_layout(self):
        self.grid = QGridLayout(self)

        layout_index = QHBoxLayout()
        layout_stock = QHBoxLayout()

        self.layout_index = layout_index
        self.layout_stock = layout_stock
        self.label_index = {}

        self.grid.addLayout(layout_index, 0, 0, 1, 2)
        self.grid.addLayout(layout_stock, 1, 0, 1, 2)

    def init_stock_layout(self):
        widget_stock = QWidget(self)
        layout_table = QHBoxLayout()
        self.table = QTableWidget(self)
        self.table.setSelectionMode(
            QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setColumnCount(len(ColumnHelper.table_col_names))
        self.table.setHorizontalHeaderLabels(ColumnHelper.table_col_names)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellDoubleClicked.connect(self.cell_double_clicked)
        layout_table.addWidget(self.table)
        widget_stock.setLayout(layout_table)
        self.layout_stock.addWidget(widget_stock)

    def cell_double_clicked(self, row, column):
        item = self.table.cellWidget(row, 0)
        stock_code = item.text()
        start_date = StockHelper.get_start_date()
        end_date = StockHelper.get_end_date()

        widget = KLineWidget(self, stock_code, start_date, end_date)
        widget.show()

    def init_index_layout(self):
        grid = QGridLayout()

        data = []

        for name in self.index_list:
            for field in ColumnHelper.index_col_names:
                data.append(StockHelper.get_index_key(name, field))

        row = 1
        column = 0
        column_count = 6

        for name in data:
            label = self.label_index.get(name)
            if not label:
                label = QLabel(name)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.label_index[name] = label

            grid.addWidget(label, row, column)

            column += 1

            if column % column_count == 0:
                row += 1
                column = 0

        self.layout_index.addLayout(grid)

    def update_index_info(self, df):
        count = df.shape[0]

        column_index_sh = 4
        column_index_sz = 5

        df_sh = self.fetch_north(StockMarket.SH)
        df_sz = self.fetch_north(StockMarket.SZ)

        for row in range(count):
            key = ''
            prefix = ''
            column = 0

            latest_price = self.get_stock_value(
                df, FieldHelper.field_latest, row)
            yclose_price = self.get_stock_value(
                df, FieldHelper.field_yclose, row)

            style = StockHelper.get_common_color(latest_price, yclose_price)

            for name in ColumnHelper.index_col_names:
                if column == column_index_sh:
                    value = self.get_north_value(df_sh)
                    style = StockHelper.get_field_color(str(value))
                elif column == column_index_sz:
                    value = self.get_north_value(df_sz)
                    style = StockHelper.get_field_color(str(value))
                else:
                    value = self.get_stock_value(df, name, row)

                label = None
                if column == 0:
                    prefix = value

                key = StockHelper.get_index_key(prefix, name)

                label = self.label_index.get(key)

                column += 1

                if not label:
                    continue

                value = str(value)

                label.setText(value)
                label.setStyleSheet(style)

    def update_stock_info(self, df):
        count = df.shape[0]
        self.table.setRowCount(count)

        for row in range(count):
            latest_price = self.get_stock_value(
                df, FieldHelper.field_latest, row)
            yclose_price = self.get_stock_value(
                df, FieldHelper.field_yclose, row)

            style = StockHelper.get_common_color(latest_price, yclose_price)

            column = 0
            for name in ColumnHelper.table_col_names:
                value = str(df[name][row])

                label = QLabel(value)
                label.setStyleSheet(style)
                self.table.setCellWidget(row, column, label)

                column += 1

    def fetch_index(self):
        return self.stock_info.fetch_index_all()

    def fetch_north(self, type):
        return self.stock_info.fetch_north(type)

    def fetch_stock(self):
        return self.stock_info.fetch_stock_all()

    def get_north_value(self, df):
        if df is None or df.empty:
            return ''

        name = 'value'

        if name not in df:
            return ''

        return df[name][0]

    def get_stock_value(self, df, name, row):
        if df is None or df.empty:
            return ''

        if name not in df:
            return ''

        return df[name][row]

