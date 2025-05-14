from pathlib import Path
import sys
import urllib.request
import random

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt


ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))


from text_encode import encode_binary_to_text
from utils.string import str_to_bits


class EncodeTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._setup_ui()

    def _setup_ui(self):
        """Инициализация интерфейса вкладки кодирования"""
        layout = QVBoxLayout(self)

        # Исходный текст
        layout.addWidget(QLabel("Исходный текст:"))

        # Кнопки загрузки
        load_buttons_layout = QHBoxLayout()

        self.load_gutenberg_btn = QPushButton("Загрузить из Gutenberg")
        self.load_gutenberg_btn.clicked.connect(self._load_from_gutenberg)
        load_buttons_layout.addWidget(self.load_gutenberg_btn)

        self.load_file_btn = QPushButton("Загрузить файл")
        self.load_file_btn.clicked.connect(self._load_from_file)
        load_buttons_layout.addWidget(self.load_file_btn)

        layout.addLayout(load_buttons_layout)

        # Поле текста
        self.source_text_area = QTextEdit()
        self.source_text_area.setAcceptRichText(False)
        self.source_text_area.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self.source_text_area)

        # Поле для сообщения
        layout.addWidget(QLabel("Сообщение для скрытия:"))
        self.message_entry = QLineEdit()
        layout.addWidget(self.message_entry)

        # Кнопка кодирования
        self.encode_btn = QPushButton("Закодировать сообщение")
        self.encode_btn.clicked.connect(self._encode_message)
        layout.addWidget(self.encode_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Результат кодирования
        layout.addWidget(QLabel("Результат:"))
        self.result_text_area = QTextEdit()
        self.result_text_area.setAcceptRichText(False)
        self.result_text_area.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self.result_text_area)

        # Кнопки для работы с результатом
        result_buttons_layout = QHBoxLayout()

        self.copy_result_btn = QPushButton("Копировать результат")
        self.copy_result_btn.clicked.connect(self._copy_result)
        result_buttons_layout.addWidget(self.copy_result_btn)

        self.save_result_btn = QPushButton("Сохранить результат")
        self.save_result_btn.clicked.connect(self._save_result)
        result_buttons_layout.addWidget(self.save_result_btn)

        layout.addLayout(result_buttons_layout)

    def _load_from_gutenberg(self):
        try:
            url = random.choice(self.parent_window.GUTENBERG_BOOKS)
            self.source_text_area.setPlainText("Идет загрузка текста...")
            QApplication.processEvents()

            with urllib.request.urlopen(url) as response:
                text = response.read().decode("utf-8")
                lines = text.split("\n")
                source_text = "\n".join(lines[:2000])
                self.source_text_area.setPlainText(source_text)
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось загрузить текст: {str(e)}"
            )

    def _load_from_file(self):
        """Загружает текст из файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл", "", "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            self.source_text_area.setPlainText(text)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def _encode_message(self):
        """Кодирует сообщение в текст"""
        message = self.message_entry.text()
        if not message:
            QMessageBox.warning(self, "Предупреждение", "Введите сообщение для скрытия")
            return

        source_text = self.source_text_area.toPlainText()
        if not source_text.strip():
            QMessageBox.warning(self, "Предупреждение", "Загрузите исходный текст")
            return

        try:
            binary_msg = str_to_bits(message)
            lines = source_text.split("\n")

            if len(lines) < len(binary_msg):
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Текст слишком короткий для этого сообщения. "
                    f"Нужно минимум {len(binary_msg)} строк.",
                )
                return

            encoded_lines = encode_binary_to_text(lines, binary_msg)
            encoded_text = "\n".join(encoded_lines)

            self.result_text_area.setPlainText(encoded_text)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при кодировании: {str(e)}")

    def _copy_result(self):
        """Копирует результат кодирования в буфер обмена"""
        text = self.result_text_area.toPlainText()
        if text.strip():
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(self, "Успех", "Текст скопирован в буфер обмена!")
        else:
            QMessageBox.warning(self, "Предупреждение", "Нет текста для копирования")

    def _save_result(self):
        """Сохраняет результат кодирования в файл"""
        result_text = self.result_text_area.toPlainText()
        if not result_text.strip():
            QMessageBox.warning(self, "Предупреждение", "Нет данных для сохранения")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*)",
            options=QFileDialog.Option.DontUseNativeDialog,
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result_text)
            QMessageBox.information(self, "Успех", "Файл успешно сохранен")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")
