from PyQt6.QtWidgets import QApplication, QTextEdit
from PyQt6.QtCore import QTimer


class SafeTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._text_queue = ""
        self._chunk_size = 10000
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._process_chunk)

    def set_large_text(self, text):
        self._text_queue = text
        self.clear()
        self._timer.start(5)

    def _process_chunk(self):
        if not self._text_queue:
            self._timer.stop()
            return

        chunk = self._text_queue[: self._chunk_size]
        self._text_queue = self._text_queue[self._chunk_size :]

        self.append(chunk)  # Добавляем по частям
        QApplication.processEvents()  # Обрабатываем другие события
