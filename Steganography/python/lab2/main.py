import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
)

from embed_tab import EmbedTab
from extract_tab import ExtractTab


def main():
    app = QApplication(sys.argv)
    window = WatermarkApp()
    window.show()
    sys.exit(app.exec())


class WatermarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Цифровой водяной знак")
        self.setGeometry(100, 100, 1280, 720)
        self.setMinimumSize(800, 600)

        self._setup_ui()

    def _setup_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.embed_tab = EmbedTab()
        self.extract_tab = ExtractTab()

        self.tabs.addTab(self.embed_tab, "Внедрение ЦВЗ")
        self.tabs.addTab(self.extract_tab, "Извлечение ЦВЗ")


if __name__ == "__main__":
    main()
