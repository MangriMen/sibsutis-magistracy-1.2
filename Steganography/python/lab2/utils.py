from PyQt6.QtWidgets import QMessageBox, QLabel, QWidget
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image


def load_image(path) -> QPixmap:
    img = Image.open(path)
    img.thumbnail((512, 512))

    if img.mode == "RGB":
        rgb_image = img.convert("RGB")
        qimage = QImage(
            rgb_image.tobytes(),
            rgb_image.size[0],
            rgb_image.size[1],
            QImage.Format.Format_RGB888,
        )
    else:
        qimage = QImage(path)

    return QPixmap.fromImage(qimage)
