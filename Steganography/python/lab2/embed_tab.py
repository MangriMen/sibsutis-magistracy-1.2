import os
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QScrollArea,
)

import digital_watermark
import utils
from image_label import ImageLabel
from safe_text_edit import SafeTextEdit


class EmbedTab(QWidget):
    def __init__(self):
        super().__init__()
        self.image_path = ""
        self.watermark_path = ""
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
        image_layout.addWidget(QLabel("Изображение:"))
        self.image_path_entry = QLineEdit()
        image_layout.addWidget(self.image_path_entry)
        browse_image_btn = QPushButton("Обзор")
        browse_image_btn.clicked.connect(self.browse_image)
        image_layout.addWidget(browse_image_btn)
        control_layout.addLayout(image_layout)

        # Ввод ЦВЗ
        watermark_layout = QHBoxLayout()
        watermark_layout.addWidget(QLabel("ЦВЗ:"))
        self.watermark_entry = QLineEdit()
        watermark_layout.addWidget(self.watermark_entry)
        browse_watermark_btn = QPushButton("Обзор")
        browse_watermark_btn.clicked.connect(self.browse_watermark)
        watermark_layout.addWidget(browse_watermark_btn)
        control_layout.addLayout(watermark_layout)

        # Кнопка внедрения
        self.embed_button = QPushButton("Внедрить ЦВЗ")
        self.embed_button.clicked.connect(self.embed)
        control_layout.addWidget(self.embed_button)

        left_layout.addWidget(control_frame)

        keys_frame = QWidget()
        keys_layout = QVBoxLayout(keys_frame)
        keys_layout.setContentsMargins(0, 0, 0, 0)  # Убираем лишние отступы
        keys_layout.setSpacing(5)  # Расстояние между элементами

        # Создаем горизонтальный контейнер для label и кнопки
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Добавляем label и кнопку с выравниванием по краям
        label = QLabel("Ключи для извлечения:")
        header_layout.addWidget(label)

        copy_btn = QPushButton("Копировать")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        header_layout.addWidget(copy_btn)

        # Добавляем растягивающий элемент между label и кнопкой
        header_layout.addStretch()

        # Добавляем горизонтальный layout в вертикальный
        keys_layout.addLayout(header_layout)

        # Создаем текстовое поле, которое займет все оставшееся пространство
        self.keys_entry = SafeTextEdit()
        self.keys_entry.setReadOnly(True)
        keys_layout.addWidget(
            self.keys_entry, stretch=1
        )  # stretch=1 для заполнения пространства

        left_layout.addWidget(keys_frame)
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

    def embed(self):
        if not self.image_path:
            QMessageBox.critical(self, "Ошибка", "Выберите изображение")
            return

        watermark_bytes = self.load_watermark_bytes()
        if not watermark_bytes:
            QMessageBox.critical(self, "Ошибка", "Введите текст водяного знака")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить изображение",
            "",
            "BMP Files (*.bmp);",
        )
        if not save_path:
            return

        try:
            embedded_img, keys = digital_watermark.embed_watermark(
                self.image_path, watermark_bytes
            )

            embedded_img.save(save_path)

            keys_str = ",".join([f"{x},{y}" for x, y in keys])
            self.keys_entry.set_large_text(keys_str)

            QMessageBox.information(self, "Успех", "Водяной знак успешно внедрен")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при внедрении:\n{str(e)}")

    def load_watermark_bytes(self):
        if os.path.exists(self.watermark_path):
            with open(self.watermark_path, "rb") as f:
                return f.read()
        else:
            return self.watermark_entry.text().encode("utf-8")

    def browse_image(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "", "Images (*.bmp);;All Files (*)"
        )
        if filepath:
            self.image_path = filepath
            self.image_path_entry.setText(filepath)
            self.display_image(filepath)

    def browse_watermark(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл с ЦВЗ", "", "All Files (*)"
        )
        if filepath:
            self.watermark_path = filepath
            self.watermark_entry.setText(filepath)

    def display_image(self, path):
        try:
            self.image_label.setPixmap(utils.load_image(path))
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось загрузить изображение:\n{str(e)}"
            )

    def copy_to_clipboard(self):
        text = self.keys_entry.toPlainText().replace("\n", "")
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Скопировано", "Ключи скопированы в буфер")
        else:
            QMessageBox.warning(self, "Пусто", "Нет ключей для копирования")
