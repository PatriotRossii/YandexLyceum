import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog


class NumItem(QTableWidgetItem):
    def __lt__(self, other: QTableWidgetItem):
        return int(self.text()) < int(other.text())


class AddDialogue(QDialog):
    def __init__(self):
        super().__init__()

        self.con = sqlite3.connect("films_db.sqlite")
        self.cur = self.con.cursor()

        uic.loadUi("add_dialogue.ui", self)
        self.genre_edit.addItems(
            [e[0] for e in self.cur.execute("SELECT title FROM genres").fetchall()]
        )

        self.init_signals()

    def get_fields(self):
        return {"title": self.title_edit.text(), "year": self.year_edit.text(), "genre": self.genre_edit.currentText(),
                "duration": self.duration_edit.text()}

    def insert_data(self, data):
        if not all(data.values()):
            self.indicator_lbl.setText("Неверно заполнена форма")
        try:
            row_id = self.cur.execute("select max(id) from films").fetchone()[0] + 1
            genre_id = self.cur.execute("SELECT id FROM genres WHERE title = ?", [data["genre"]]).fetchone()[0]
            self.cur.execute("INSERT INTO films(id, title, year, genre, duration) VALUES(?, ?, ?, ?, ?)", [
                row_id, data["title"], data["year"], genre_id, data["duration"]
            ])
            self.con.commit()
            self.accept()
        except sqlite3.Error:
            self.indicator_lbl.setText("Неверные данные")

    def init_signals(self):
        self.submit_btn.clicked.connect(lambda: self.insert_data(self.get_fields()))


class Example(QMainWindow):
    def __init__(self):
        super().__init__()

        self.con = sqlite3.connect("films_db.sqlite")
        self.cur = self.con.cursor()

        self.headings = ["ИД", "Название фильма", "Год выпуска", "Жанр", "Продолжительность"]
        self.count_of_headings = len(self.headings)

        uic.loadUi("UI.ui", self)

        self.init_signals()

        self.refresh_table()

    def init_signals(self):
        self.pushButton.clicked.connect(self.open_dialogue)

    def closeEvent(self, event):
        self.con.close()

    def open_dialogue(self):
        dialogue = AddDialogue()
        dialogue.exec_() and self.refresh_table()

    def refresh_table(self):
        self.tableWidget.clear()

        data = self.cur.execute("SELECT films.id, films.title, year, genres.title, duration FROM films INNER JOIN"
                                " genres ON genres.id = films.genre").fetchall()

        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(self.count_of_headings)
        self.tableWidget.setHorizontalHeaderLabels(self.headings)

        for idx, element in enumerate(data):
            element = [str(e) for e in element]

            self.tableWidget.setItem(idx, 0, NumItem(element[0]))
            self.tableWidget.setItem(idx, 1, QTableWidgetItem(element[1]))
            self.tableWidget.setItem(idx, 2, QTableWidgetItem(element[2]))
            self.tableWidget.setItem(idx, 3, QTableWidgetItem(element[3]))
            self.tableWidget.setItem(idx, 4, QTableWidgetItem(element[4]))

        self.tableWidget.sortItems(0, Qt.DescendingOrder)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
