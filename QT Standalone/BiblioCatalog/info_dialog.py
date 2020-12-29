from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel


class InfoDialog(QDialog):

    def __init__(self, name, author, year, genre, img_src=None, parent=None):
        super(InfoDialog, self).__init__(parent)

        font = QFont("Arial", 36, QFont.Bold)

        self.setWindowTitle(name)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()

        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)
        img_pixmap = QPixmap()
        img_pixmap.load("resources/standard_image.png" if not img_src else img_src)

        img_pixmap = img_pixmap.scaled(200, 200)
        img_label.setPixmap(img_pixmap)

        self.layout.addWidget(img_label)

        name_label = QLabel("Название")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setFont(font)

        self.layout.addWidget(name_label)

        name_content_label = QLabel(name)
        name_content_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(name_content_label)

        author_label = QLabel("Автор")
        author_label.setAlignment(Qt.AlignCenter)
        author_label.setFont(font)

        self.layout.addWidget(author_label)

        author_content_label = QLabel(author)
        author_content_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(author_content_label)

        year_label = QLabel("Год выпуска")
        year_label.setAlignment(Qt.AlignCenter)
        year_label.setFont(font)

        self.layout.addWidget(year_label)

        year_content_label = QLabel(str(year))
        year_content_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(year_content_label)

        genre_label = QLabel("Жанр")
        genre_label.setAlignment(Qt.AlignCenter)
        genre_label.setFont(font)

        self.layout.addWidget(genre_label)

        genre_content_label = QLabel(genre)
        genre_content_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(genre_content_label)

        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)
