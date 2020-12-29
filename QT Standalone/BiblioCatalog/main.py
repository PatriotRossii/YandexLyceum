import sqlite3
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QListWidget, QHBoxLayout, QPushButton, \
    QComboBox, QLineEdit, QListWidgetItem
from info_dialog import InfoDialog


class Example(QMainWindow):
    def __init__(self):
        super().__init__()

        self.conn = sqlite3.connect("catalog.db")
        self.cur = self.conn.cursor()

        self.init_ui()
        self.init_signals()

    def init_ui(self):
        self.setWindowTitle('Каталог библиотеки')

        main_layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.result_widget = QListWidget()

        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.result_widget)

        params_layout = QVBoxLayout()
        self.search_btn = QPushButton("Искать")

        input_layout.addLayout(params_layout)
        input_layout.addWidget(self.search_btn)

        self.search_by = QComboBox()
        self.search_by.addItems([
            "Автор", "Название"
        ])
        self.search_edit = QLineEdit()

        params_layout.addWidget(self.search_by)
        params_layout.addWidget(self.search_edit)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def init_signals(self):
        self.search_btn.clicked.connect(lambda: self.insert(self.search(*self.parse_data())))
        self.result_widget.itemActivated.connect(lambda e: self.open_dialog(*self.get_data(e)))

    def parse_data(self) -> (str, str):
        return self.search_by.currentText(), self.search_edit.text()

    def search(self, parameter: str, value: str):
        if parameter == "Автор":
            return self.cur.execute(f"SELECT books.id, books.name FROM books INNER JOIN authors ON "
                                    f"books.author_id == authors.id"
                                    f" WHERE authors.name LIKE "
                                    f"'%{value}%'").fetchall()
        elif parameter == "Название":
            return self.cur.execute(f"SELECT id, name FROM books WHERE name LIKE '%{value}%'")
        return []

    def insert(self, data):
        self.result_widget.clear()
        for element in data:
            list_item = QListWidgetItem(element[1])
            list_item.setData(Qt.UserRole, element[0])

            self.result_widget.addItem(list_item)

    def get_data(self, item):
        return self.cur.execute("SELECT books.name, authors.name, year, genres.name, img_src "
                                "FROM books INNER JOIN authors "
                                "ON authors.id = books.author_id INNER JOIN genres ON books.genre_id = genres.id "
                                f"WHERE books.id = {item.data(Qt.UserRole)}").fetchone()

    def open_dialog(self, *args):
        dialog = InfoDialog(*args)
        dialog.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())