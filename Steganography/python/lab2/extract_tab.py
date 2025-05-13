from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QScrollArea,
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from PIL import Image

import digital_watermark
import utils
from image_label import ImageLabel
from safe_text_edit import SafeTextEdit


class ExtractTab(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)

        # Левая панель (управление)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Панель управления
        control_frame = QWidget()
        control_layout = QVBoxLayout(control_frame)

        # Выбор изображения
        image_layout = QHBoxLayout()
        image_layout.addWidget(QLabel("Файл изображения:"))
        self.image_path_entry = QLineEdit()
        image_layout.addWidget(self.image_path_entry)
        browse_btn = QPushButton("Обзор")
        browse_btn.clicked.connect(self.browse_image)
        image_layout.addWidget(browse_btn)
        control_layout.addLayout(image_layout)

        # Ключи
        keys_layout = QHBoxLayout()
        keys_layout.addWidget(QLabel("Ключи:"))
        self.keys_entry = SafeTextEdit()
        keys_layout.addWidget(self.keys_entry)
        control_layout.addLayout(keys_layout)

        # Кнопка извлечения
        self.extract_button = QPushButton("Извлечь ЦВЗ")
        self.extract_button.clicked.connect(self.extract)
        control_layout.addWidget(self.extract_button)

        left_layout.addWidget(control_frame)

        # Результат (извлеченный текст)
        result_frame = QWidget()
        result_layout = QVBoxLayout(result_frame)
        result_layout.addWidget(QLabel("Извлеченный текст:"))

        self.extracted_text = SafeTextEdit()
        self.extracted_text.setReadOnly(True)
        result_layout.addWidget(self.extracted_text)

        left_layout.addWidget(result_frame)
        left_layout.addStretch()

        main_layout.addWidget(left_panel)

        # Правая панель (изображение)
        right_panel = QWidget()
        right_panel.setMinimumSize(512, 512)

        right_layout = QVBoxLayout(right_panel)

        self.image_label = ImageLabel()

        scroll = QScrollArea()
        scroll.setWidget(self.image_label)
        scroll.setWidgetResizable(True)
        right_layout.addWidget(scroll)

        main_layout.addWidget(right_panel)

    def extract(self):
        image_path = self.image_path_entry.text()

        if not image_path:
            QMessageBox.critical(self, "Ошибка", "Выберите изображение")
            return

        try:
            keys_string = self.keys_entry.toPlainText().replace("\n", "")
            if not keys_string:
                QMessageBox.critical(self, "Ошибка", "Введите ключи")
                return

            numbers = list(map(int, keys_string.split(",")))

            if len(numbers) % 2 != 0:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    "Неверный формат ключей. Ожидались пары чисел",
                )
                return

            coord_pairs = list(zip(numbers[::2], numbers[1::2]))
            extracted_bits = digital_watermark.extract_watermark(
                image_path, coord_pairs
            )

            bit_string = "".join(map(str, extracted_bits))
            bytes_list = [
                int(bit_string[i : i + 8], 2) for i in range(0, len(bit_string), 8)
            ]
            extracted_text = bytes(bytes_list).decode("utf-8", errors="replace")

            self.extracted_text.set_large_text(extracted_text or "Текст не найден")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при извлечении:\n{str(e)}")

    def browse_image(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "", "Images (*.bmp);;All Files (*)"
        )
        if filepath:
            self.image_path_entry.setText(filepath)
            self.display_image(filepath)

    def display_image(self, path):
        try:
            self.image_label.setPixmap(utils.load_image(path))
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось загрузить изображение:\n{str(e)}"
            )
