# UNDONE

"""
Вспомним PIL. Напишите программу с графическим пользовательским интерфейсом на PyQT. При старте приложения должен открываться диалог выбора изображения. В программу загружается квадратная картинка. Необходимо реализовать следующие возможности:

Оставить один из цветовых каналов
Повернуть картинку на 90 градусов влево/вправо
Все изменения должны быть видны в реальном времени.
"""

import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QPushButton, QWidget

from PyQt5 import QtGui

from PIL import Image
from PIL.ImageQt import ImageQt


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PIL 2.0')

        self.r_btn = QPushButton("R")
        self.r_btn.clicked.connect(lambda: self.show_im("R"))

        self.g_btn = QPushButton("G")
        self.g_btn.clicked.connect(lambda: self.show_im("G"))

        self.b_btn = QPushButton("B")
        self.b_btn.clicked.connect(lambda: self.show_im("B"))

        self.a_btn = QPushButton("ALL")
        self.a_btn.clicked.connect(lambda: self.show_im("A"))

        self.left_btn = QPushButton("Против часовой стрелки")
        self.left_btn.clicked.connect(lambda: self.turn(False))

        self.right_btn = QPushButton("По часовой стрелки")
        self.right_btn.clicked.connect(lambda: self.turn(True))

        self.pixmap = QPixmap()
        self.image = QLabel(self)
        self.image.setPixmap(self.pixmap)

        main_layout = QVBoxLayout()
        functional_layout = QHBoxLayout()
        buttons_layout = QVBoxLayout()
        turn_layout = QHBoxLayout()

        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

        main_layout.addLayout(functional_layout)
        main_layout.addLayout(turn_layout)

        functional_layout.addLayout(buttons_layout)
        functional_layout.addWidget(self.image)

        buttons_layout.addWidget(self.r_btn)
        buttons_layout.addWidget(self.g_btn)
        buttons_layout.addWidget(self.b_btn)
        buttons_layout.addWidget(self.a_btn)

        turn_layout.addWidget(self.left_btn)
        turn_layout.addWidget(self.right_btn)

        self.initialize_image()

    def initialize_image(self):
        fileName = QFileDialog.getOpenFileName(self, "Open Image",
                                               "/home/",
                                               "Image Files (*.png *.jpg *.bmp)")

        if fileName[0]:
            fileName = fileName[0]

            self.im = Image.open(fileName).convert("RGB")
            self.r, self.g, self.b = self.im.split()

            r_b, g_b, b_b = Image.new("RGB", self.im.size, (0, 0, 0)).split()

            self.r = QtGui.QPixmap.fromImage(ImageQt(Image.merge("RGB", (self.r, g_b, b_b))))
            self.g = QtGui.QPixmap.fromImage(ImageQt(Image.merge("RGB", (r_b, self.g, b_b))))
            self.b = QtGui.QPixmap.fromImage(ImageQt(Image.merge("RGB", (r_b, g_b, self.b))))
            self.im = QPixmap(fileName)

            self.image.setPixmap(self.im)
        else:
            sys.exit()

    def show_im(self, channel):
        if channel == "A":
            self.image.setPixmap(self.im)
        elif channel == "R":
            self.image.setPixmap(self.r)
        elif channel == "G":
            self.image.setPixmap(self.g)
        elif channel == "B":
            self.image.setPixmap(self.b)

    def turn(self, right):
        if right:
            self.im = self.im.rotate(-90)
        else:
            self.im = self.im.rotate(90)

        self.pixmap = QtGui.QPixmap.fromImage(ImageQt(self.im))
        self.image.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())