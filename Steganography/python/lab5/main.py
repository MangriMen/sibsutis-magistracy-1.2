import sys

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
)
from PyQt6.QtCore import QSize

from decode_tab import DecodeTab
from encode_tab import EncodeTab


def main():
    app = QApplication(sys.argv)
    window = TextSteganographyApp()
    window.show()
    sys.exit(app.exec())


class TextSteganographyApp(QMainWindow):
    GUTENBERG_BOOKS = [
        "https://dev.gutenberg.org/files/1342/1342-0.txt",  # Pride and Prejudice
        "https://dev.gutenberg.org/files/11/11-0.txt",  # Alice's Adventures in Wonderland
        "https://dev.gutenberg.org/files/2701/2701-0.txt",  # Moby Dick
        "https://dev.gutenberg.org/files/84/84-0.txt",  # Frankenstein
        "https://dev.gutenberg.org/files/98/98-0.txt",  # A Tale of Two Cities
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Текстовая стеганография")
        self.setMinimumSize(QSize(900, 800))
        self._setup_ui()

    def _setup_ui(self):
        """Инициализация главного окна"""
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Создаем и добавляем вкладки
        self.encode_tab = EncodeTab(self)
        self.decode_tab = DecodeTab(self)

        self.tab_widget.addTab(self.encode_tab, "Кодирование")
        self.tab_widget.addTab(self.decode_tab, "Декодирование")


if __name__ == "__main__":
    main()
