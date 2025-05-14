from PyQt6.QtWidgets import (
    QLabel,
)
from PyQt6.QtCore import Qt


class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(1, 1)  # Минимальный размер
        self.original_pixmap = None

    def setPixmap(self, pixmap):
        self.original_pixmap = pixmap
        self.resize_image()

    def resizeEvent(self, event):
        self.resize_image()
        super().resizeEvent(event)

    def resize_image(self):
        if self.original_pixmap:
            scaled = self.original_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            super().setPixmap(scaled)
