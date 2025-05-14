from pathlib import Path
import sys
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


from text_encode import extract_binary_from_text
from utils.string import bits_to_str


class DecodeTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        load_buttons_layout = QHBoxLayout()

        self.load_encoded_btn = QPushButton("Загрузить файл")
        self.load_encoded_btn.clicked.connect(self._load_encoded_file)
        load_buttons_layout.addWidget(self.load_encoded_btn)

        self.paste_btn = QPushButton("Вставить")
        self.paste_btn.clicked.connect(self._paste_from_clipboard)
        load_buttons_layout.addWidget(self.paste_btn)

        layout.addLayout(load_buttons_layout)

        layout.addWidget(QLabel("Текст со скрытым сообщением:"))
        self.encoded_text_area = QTextEdit()
        self.encoded_text_area.setAcceptRichText(False)
        self.encoded_text_area.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self.encoded_text_area)

        self.decode_btn = QPushButton("Декодировать сообщение")
        self.decode_btn.clicked.connect(self._decode_message)
        layout.addWidget(self.decode_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(QLabel("Извлеченное сообщение:"))
        self.decoded_message_entry = QLineEdit()
        layout.addWidget(self.decoded_message_entry)

    def _load_encoded_file(self):
        """Загружает закодированный текст из файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл", "", "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            self.encoded_text_area.setPlainText(text)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def _paste_from_clipboard(self):
        """Вставляет текст из буфера обмена"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.encoded_text_area.setPlainText(text)
        else:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Буфер обмена пуст или содержит не текстовые данные",
            )

    def _decode_message(self):
        """Декодирует сообщение из текста"""
        encoded_text = self.encoded_text_area.toPlainText()
        if not encoded_text.strip():
            QMessageBox.warning(
                self, "Предупреждение", "Загрузите текст со скрытым сообщением"
            )
            return

        try:
            binary_msg = extract_binary_from_text(encoded_text)
            message = bits_to_str(binary_msg)

            self.decoded_message_entry.setText(message)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при декодировании: {str(e)}")
