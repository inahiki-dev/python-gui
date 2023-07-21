import sys

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, pyqtSlot, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QLineEdit
from PyQt5.QtWidgets import QPushButton

from math import *

font = QFont("JetBrains", 13)
graphWindow = None
errorWindow = None

# Функция получения числового значения для коэффициентов a1, b1, c1 и a2, b2, c2
def get(lineEdit, name):
    text = lineEdit.text()
    try:
        return float(text)
    except ValueError:
        raise ValueError(name)

# Класс основного окна
class MainWindow(QMainWindow):
    plot = None
    a1_edit = None
    b1_edit = None
    c1_edit = None
    u1_edit = None
    a2_edit = None
    b2_edit = None
    c2_edit = None
    u2_edit = None

    def __init__(self):
        super().__init__()
        self.plotWidget = None
        self.setWindowTitle("Модель хищник-жертва")
        self.setFont(font)
        self.UiComponents()

    # Функция отображения виджетов
    def UiComponents(self):
        widget = QWidget()
        layout = QGridLayout()

        plotwidget_xy = self.createPlot('y', 'x')
        plotwidget_t = self.createPlot('x (red), y (blue)', 't')

        button = self.createButton()

        xs = 100
        ys = 120
        dx = 130
        dy = 40
        self.a1_edit = self.createQEdit('a1', '1.0 ')
        self.b1_edit = self.createQEdit('b1', '0.5')
        self.c1_edit = self.createQEdit('c1', '0.0')
        self.u1_edit = self.createQEdit('u1', '0.0')
        self.a2_edit = self.createQEdit('a2', '0.5')
        self.b2_edit = self.createQEdit('b2', '2.0')
        self.c2_edit = self.createQEdit('c2', '0.0')
        self.u2_edit = self.createQEdit('u2', '0.0')

        desc_1 = self.createLabel('dx/dt = a1*x - b1*x*y - c1*x*x + u1')
        desc_2 = self.createLabel('dy/dt = - a1*y + b2*x*y - c2*y*y + u2')
        desc_a1 = self.createLabel('a1 = ')
        desc_b1 = self.createLabel('b1 = ')
        desc_c1 = self.createLabel('c1 = ')
        desc_u1 = self.createLabel('u1 = ')
        desc_a2 = self.createLabel('a2 = ')
        desc_b2 = self.createLabel('b2 = ')
        desc_c2 = self.createLabel('c2 = ')
        desc_u2 = self.createLabel('u2 = ')

        layout.addWidget(desc_1, 0, 0, 1, 0, Qt.AlignCenter)
        layout.addWidget(desc_2, 1, 0, 1, 0, Qt.AlignCenter)

        layout.addWidget(desc_a1, 2, 0)
        layout.addWidget(self.a1_edit, 2, 1)
        layout.addWidget(desc_b1, 2, 2)
        layout.addWidget(self.b1_edit, 2, 3)
        layout.addWidget(desc_c1, 2, 4)
        layout.addWidget(self.c1_edit, 2, 5)
        layout.addWidget(desc_u1, 2, 6)
        layout.addWidget(self.u1_edit, 2, 7)

        layout.addWidget(desc_a2, 3, 0)
        layout.addWidget(self.a2_edit, 3, 1)
        layout.addWidget(desc_b2, 3, 2)
        layout.addWidget(self.b2_edit, 3, 3)
        layout.addWidget(desc_c2, 3, 4)
        layout.addWidget(self.c2_edit, 3, 5)
        layout.addWidget(desc_u2, 3, 6)
        layout.addWidget(self.u2_edit, 3, 7)

        layout.addWidget(button, 4, 0, 1, 0)
        layout.addWidget(plotwidget_xy, 5, 0, 1, 0)
        layout.addWidget(plotwidget_t, 6, 0, 1, 0)

        layout.setContentsMargins(25, 25, 25, 25)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        gree_pen = pg.mkPen(color=(55, 55, 55), width=3)
        red_pen = pg.mkPen(color=(255, 0, 0), width=3)
        blue_pen = pg.mkPen(color=(0, 0, 255), width=3)
        self.plot_xy = plotwidget_xy.plot([], [], pen=gree_pen)
        self.plot_tx = plotwidget_t.plot([], [], pen=red_pen)
        self.plot_ty = plotwidget_t.plot([], [], pen=blue_pen)

    # Функция создания виджета PlotWidget
    def createPlot(self, left, bottom):
        styles = {'color': '#777777', 'font-size': '15px'}
        plotwidget = pg.PlotWidget()
        plotwidget.setLabel('left', left, **styles)
        plotwidget.setLabel('bottom', bottom, **styles)
        plotwidget.showGrid(x=True, y=True)
        plotwidget.setBackground('w')
        return plotwidget

    # Функция создания виджета QLineEdit
    def createQEdit(self, name, sv):
        lineedit = QLineEdit('0', self)
        lineedit.setObjectName(name)
        lineedit.setText(sv)
        return lineedit

    # Функция создания виджета QLabel
    def createLabel(self, text):
        label = QLabel(self)
        label.setText(text)
        return label

    # Функция создания кнопки
    def createButton(self):
        button = QPushButton('Построить график', self)
        button.clicked.connect(self.onClick)
        return button

    # Функция при нажатии на кнопку
    @pyqtSlot()
    def onClick(self):
        try:
            a1 = get(self.a1_edit, 'a1')
            b1 = get(self.b1_edit, 'b1')
            c1 = get(self.c1_edit, 'c1')
            u1 = self.u1_edit.text()
            a2 = get(self.a2_edit, 'a2')
            b2 = get(self.b2_edit, 'b2')
            c2 = get(self.c2_edit, 'c2')
            u2 = self.u2_edit.text()
            self.printPlot(a1, b1, c1, u1, a2, b2, c2, u2)
        except ValueError as e:
            error('Указано некорректное значение для коэффициента ' + e.args[0])

    # Функция отрисовки графика
    def printPlot(self, a1, b1, c1, u1, a2, b2, c2, u2):

        # Метод Рунге-Кутта 4-го порядка
        def rungeKutta4order(r, t, h):
            k1 = h * dxdy(r, t)
            k2 = h * dxdy(r + 0.5 * k1, t + 0.5 * h)
            k3 = h * dxdy(r + 0.5 * k2, t + 0.5 * h)
            k4 = h * dxdy(r + k3, t + h)
            return (k1 + 2 * k2 + 2 * k3 + k4) / 6

        # Получение значений из функций в виде массива 2x1
        # Параметр t не является обязательным, так как в нашем уравнении нет данного параметра
        def dxdy(r, t):
            x, y = r[0], r[1]
            fxd = a1 * x - b1 * x * y - c1 * x * x + eval(u1, {"x": x, "y": y}, globals())
            fyd = - a2 * y + b2 * x * y - c2 * y * y + eval(u2, {"x": x, "y": y}, globals())
            return np.array([fxd, fyd], float)

        h = 0.01
        cur = np.array([2, 2], float)
        t_arr = np.arange(0, 30, h)
        x_arr = []
        y_arr = []
        try:
            for t in t_arr:
                x_arr.append(cur[0])
                y_arr.append(cur[1])
                cur += rungeKutta4order(cur, t, h)

            self.plot_xy.setData(x_arr, y_arr)
            self.plot_tx.setData(t_arr, x_arr)
            self.plot_ty.setData(t_arr, y_arr)
        except SyntaxError as e:
            error('Указан неверный синтаксис: ' + e.text)
        except NameError as e:
            error('Не удалось найти функцию: ' + e.name)


# Класс окна с ошибкой
class ErrorWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(ErrorWindow, self).__init__(*args, **kwargs)
        self.setMinimumSize(QSize(450, 145))
        self.setWindowTitle("Ошибка")
        self.setFont(font)

        self.errLabel = QLabel(self)
        self.errLabel.setAlignment(Qt.AlignCenter)
        pybutton = QPushButton('Ок', self)
        pybutton.clicked.connect(self.onClick)

        layout = QGridLayout()
        layout.addWidget(self.errLabel, 0, 0, 1, 5)
        layout.addWidget(pybutton, 1, 2)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    @pyqtSlot()
    def onClick(self):
        self.hide()
        self.errLabel.setText('')

# Функция вызова окна с ошибкой
def error(text):
    errorWindow.hide()
    errorWindow.errLabel.setText(text)
    pos = mainWindow.pos()
    x = pos.x() + int(mainWindow.geometry().width() / 2) - 225
    y = pos.y() + int(mainWindow.geometry().height() / 2) - 73
    errorWindow.move(x, y)
    errorWindow.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.show()

    errorWindow = ErrorWindow()
    errorWindow.hide()

    sys.exit(app.exec_())
