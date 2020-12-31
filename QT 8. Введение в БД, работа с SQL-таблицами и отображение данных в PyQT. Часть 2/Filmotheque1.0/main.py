import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog, QTableWidget


class NumItem(QTableWidgetItem):
    def __lt__(self, other: QTableWidgetItem):
        return int(self.text()) < int(other.text())


class AddFilmDialogue(QDialog):
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

        self.films_headings = ["ИД", "Название фильма", "Год выпуска", "Жанр", "Продолжительность"]
        self.count_of_films_headings = len(self.films_headings)

        self.genres_headings = ["ИД", "Название жанра"]
        self.count_of_genres_headings = len(self.genres_headings)

        uic.loadUi("UI.ui", self)

        self.init_signals()

        self.refresh_films_table()
        self.refresh_genres_table()

    def init_signals(self):
        self.add_film_btn.clicked.connect(self.open_add_film_dialogue)

    def closeEvent(self, event):
        self.con.close()

    def open_add_film_dialogue(self):
        dialogue = AddFilmDialogue()
        dialogue.exec_() and self.refresh_films_table()

    def refresh_films_table(self):
        self.films_table_widget.clear()

        data = self.cur.execute("SELECT films.id, films.title, year, genres.title, duration FROM films INNER JOIN"
                                " genres ON genres.id = films.genre").fetchall()

        self.films_table_widget.setRowCount(len(data))
        self.films_table_widget.setColumnCount(self.count_of_films_headings)
        self.films_table_widget.setHorizontalHeaderLabels(self.films_headings)

        for idx, element in enumerate(data):
            element = [str(e) for e in element]

            self.films_table_widget.setItem(idx, 0, NumItem(element[0]))
            self.films_table_widget.setItem(idx, 1, QTableWidgetItem(element[1]))
            self.films_table_widget.setItem(idx, 2, QTableWidgetItem(element[2]))
            self.films_table_widget.setItem(idx, 3, QTableWidgetItem(element[3]))
            self.films_table_widget.setItem(idx, 4, QTableWidgetItem(element[4]))

        self.films_table_widget.sortItems(0, Qt.DescendingOrder)

    def refresh_genres_table(self):
        self.genres_table_widget.clear()

        data = self.cur.execute("SELECT id, title FROM genres").fetchall()

        self.genres_table_widget.setRowCount(len(data))
        self.genres_table_widget.setColumnCount(self.count_of_genres_headings)
        self.genres_table_widget.setHorizontalHeaderLabels(self.genres_headings)

        for idx, element in enumerate(data):
            element = [str(e) for e in element]

            self.genres_table_widget.setItem(idx, 0, NumItem(element[0]))
            self.genres_table_widget.setItem(idx, 1, QTableWidgetItem(element[1]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
