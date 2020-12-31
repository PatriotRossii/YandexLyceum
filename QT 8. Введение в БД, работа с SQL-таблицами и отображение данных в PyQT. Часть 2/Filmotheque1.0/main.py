import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog, QTableWidget


class NumItem(QTableWidgetItem):
    def __lt__(self, other: QTableWidgetItem):
        return int(self.text()) < int(other.text())


class AddUpdateFilmDialogue(QDialog):
    def __init__(self, update=False, film_id=None):
        super().__init__()

        self.film_id = film_id
        self.update = update

        self.con = sqlite3.connect("films_db.sqlite")
        self.cur = self.con.cursor()

        uic.loadUi("add_film_dialogue.ui", self)

        self.genre_edit.addItems(
            [e[0] for e in self.cur.execute("SELECT title FROM genres").fetchall()]
        )
        if update:
            self.setWindowTitle("Обновить фильм")
            self.submit_btn.setText("Сохранить")
            self.init_fields(self.get_data())

        self.init_signals()

    def init_fields(self, data):
        self.title_edit.setText(data["title"])
        self.year_edit.setText(str(data["year"]))
        self.genre_edit.setCurrentText(data["genre"])
        self.duration_edit.setText(str(data["duration"]))

    def get_data(self):
        data = self.cur.execute("SELECT films.title, year, genres.title, duration FROM films INNER JOIN genres ON "
                                "films.genre = genres.id WHERE films.id = ?", [self.film_id]).fetchone()
        return {"title": data[0], "year": data[1], "genre": data[2], "duration": data[3]}

    def get_fields(self):
        row_id = self.cur.execute("select max(id) from films").fetchone()[0] + 1 if not self.update else self.film_id
        genre_id = self.cur.execute("SELECT id FROM genres WHERE title = ?", [self.genre_edit.currentText()])\
            .fetchone()[0]

        return {"id": row_id, "title": self.title_edit.text(), "year": self.year_edit.text(), "genre": genre_id,
                "duration": self.duration_edit.text()}

    def catch_errors(self, fn, data):
        if not all(data.values()):
            self.indicator_lbl.setText("Неверно заполнена форма")
        try:
            fn(self, data)
        except sqlite3.Error:
            self.indicator_lbl.setText("Неверные данные")

    def insert_data(self, data):
        def insert_fn(self, data):
            self.cur.execute("INSERT INTO films(id, title, year, genre, duration) VALUES(?, ?, ?, ?, ?)", [
                data["id"], data["title"], data["year"], data["genre"], data["duration"]
            ])
            self.con.commit()
            self.accept()

        self.catch_errors(
            insert_fn, data
        )

    def update_data(self, data):
        def update_fn(self, data):
            self.cur.execute("UPDATE films SET title = ?, year = ?, genre = ?, duration = ? WHERE id = ?", [
                data["title"], data["year"], data["genre"], data["duration"], data["id"]
            ])
            self.con.commit()
            self.accept()
        self.catch_errors(
            update_fn, data
        )

    def init_signals(self):
        if self.update:
            self.submit_btn.clicked.connect(lambda: self.update_data(self.get_fields()))
        else:
            self.submit_btn.clicked.connect(lambda: self.insert_data(self.get_fields()))


class AddUpdateGenreDialogue(QDialog):
    def __init__(self, update=False, genre_id=None):
        super().__init__()

        self.genre_id = genre_id
        self.update = update

        self.con = sqlite3.connect("films_db.sqlite")
        self.cur = self.con.cursor()

        uic.loadUi("add_genre_dialogue.ui", self)

        if update:
            self.setWindowTitle("Обновить жанр")
            self.submit_btn.setText("Сохранить")
            self.init_fields(self.get_data())

        self.init_signals()

    def init_fields(self, data):
        self.title_edit.setText(data["title"])

    def get_data(self):
        data = self.cur.execute("SELECT title FROM genres WHERE id = ?", [self.genre_id]).fetchone()
        return {"title": data[0]}

    def get_fields(self):
        row_id = self.cur.execute("select max(id) from genres").fetchone()[0] + 1 if not self.update else self.genre_id
        return {"id": row_id, "title": self.title_edit.text()}

    def catch_errors(self, fn, data):
        if not all(data.values()):
            self.indicator_lbl.setText("Неверно заполнена форма")
        try:
            fn(self, data)
        except sqlite3.Error:
            self.indicator_lbl.setText("Неверные данные")

    def insert_data(self, data):
        def insert_fn(self, data):
            self.cur.execute("INSERT INTO genres(id, title) VALUES(?, ?)", [
                data["id"], data["title"]
            ])
            self.con.commit()
            self.accept()

        self.catch_errors(
            insert_fn, data
        )

    def update_data(self, data):
        def update_fn(self, data):
            self.cur.execute("UPDATE genres SET title = ? WHERE id = ?", [
                data["title"], data["id"]
            ])
            self.con.commit()
            self.accept()
        self.catch_errors(
            update_fn, data
        )

    def init_signals(self):
        if self.update:
            self.submit_btn.clicked.connect(lambda: self.update_data(self.get_fields()))
        else:
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
        self.edit_film_btn.clicked.connect(self.open_edit_film_dialogue)
        self.remove_film_btn.clicked.connect(self.remove_film)

        self.add_genre_btn.clicked.connect(self.open_add_genre_dialogue)
        self.edit_genre_btn.clicked.connect(self.open_edit_film_dialogue)
        self.remove_genre_btn.clicked.connect(self.remove_genre)

    def remove_film(self):
        current_row = self.films_table_widget.currentRow()

        if current_row == -1:
            return

        film_id = self.films_table_widget.item(current_row, 0).text()
        self.cur.execute("DELETE FROM films WHERE id = ?", [film_id])
        self.con.commit()

        self.films_table_widget.removeRow(current_row)

    def remove_genre(self):
        current_row = self.genres_table_widget.currentRow()

        if current_row == -1:
            return

        genre_id = self.genres_table_widget.item(current_row, 0).text()
        self.cur.execute("DELETE FROM genres WHERE id = ?", [genre_id])
        self.con.commit()

        self.genres_table_widget.removeRow(current_row)

    def closeEvent(self, event):
        self.con.close()

    def open_add_film_dialogue(self):
        dialogue = AddUpdateFilmDialogue()
        dialogue.exec_() and self.refresh_films_table()

    def open_edit_film_dialogue(self):
        current_row = self.films_table_widget.currentRow()

        if current_row == -1:
            return

        film_id = self.films_table_widget.item(current_row, 0).text()

        dialogue = AddUpdateFilmDialogue(update=True, film_id=film_id)
        dialogue.exec_() and self.refresh_films_table()

    def open_add_genre_dialogue(self):
        dialogue = AddUpdateGenreDialogue()
        dialogue.exec_() and self.refresh_genres_table()

    def open_edit_film_dialogue(self):
        current_row = self.genres_table_widget.currentRow()

        if current_row == -1:
            return

        genre_id = self.genres_table_widget.item(current_row, 0).text()
        dialogue = AddUpdateGenreDialogue(update=True, genre_id=genre_id)
        dialogue.exec_() and self.refresh_genres_table()

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
