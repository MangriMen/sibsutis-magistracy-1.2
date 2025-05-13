from PIL import Image
import numpy as np


def text_to_bitstring(text: str) -> str:
    return ''.join(f'{ord(c):08b}' for c in text)


def bitstring_to_text(bits: str) -> str:
    chars = [chr(int(bits[i:i + 8], 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)


def inp_scale(image:
   Image.Image) -> np.ndarray:
    """Увеличивает изображение с помощью INP (градации серого)"""
    original = np.array(image.convert("L"))
    h, w = original.shape
    new_h, new_w = h * 2 - 1, w * 2 - 1
    result = np.zeros((new_h, new_w), dtype=np.uint8)

    # Копируем оригинальные пиксели
    for i in range(h):
        for j in range(w):
            result[2 * i, 2 * j] = original[i, j]

    # Горизонтальная интерполяция
    for i in range(0, new_h, 2):
        for j in range(1, new_w, 2):
            left = result[i, j - 1]
            right = result[i, j + 1] if j + 1 < new_w else left
            result[i, j] = (int(left) + int(right)) // 2

    # Вертикальная интерполяция
    for i in range(1, new_h, 2):
        for j in range(0, new_w, 2):
            top = result[i - 1, j]
            bottom = result[i + 1, j] if i + 1 < new_h else top
            result[i, j] = (int(top) + int(bottom)) // 2

    # Диагональная интерполяция
    for i in range(1, new_h, 2):
        for j in range(1, new_w, 2):
            tl = result[i - 1, j - 1]
            tr = result[i - 1, j + 1] if j + 1 < new_w else tl
            bl = result[i + 1, j - 1] if i + 1 < new_h else tl
            br = result[i + 1, j + 1] if (i + 1 < new_h and j + 1 < new_w) else tl
            result[i, j] = (int(tl) + int(tr) + int(bl) + int(br)) // 4

    return result


def embed_bits_in_pixel(value: int, bits: str) -> int:
    k = len(bits)
    mask = (1 << k) - 1
    value = int(value) & 0xFF  # гарантируем uint8
    cleared = value & (~mask & 0xFF)  # безопасное обнуление младших битов
    return cleared | int(bits, 2)


def embed_message(image: Image.Image, message: str, k: int = 2) -> Image.Image:
    bits = text_to_bitstring(message)
    scaled = inp_scale(image)
    h, w = scaled.shape

    bit_index = 0
    max_bits = (h * w) // 4 * k  # приблизительно 1/4 пикселей — интерполированные

    if len(bits) > max_bits:
        raise ValueError("Сообщение слишком длинное для данного изображения")

    # Встраиваем только в интерполированные пиксели
    for i in range(h):
        for j in range(w):
            if i % 2 != 0 or j % 2 != 0:
                if bit_index + k <= len(bits):
                    chunk = bits[bit_index:bit_index + k]
                    scaled[i, j] = embed_bits_in_pixel(scaled[i, j], chunk)
                    bit_index += k
                else:
                    break

    return Image.fromarray(scaled)


def extract_message(image: Image.Image, length: int, k: int = 2) -> str:
    img = np.array(image.convert("L"))
    h, w = img.shape
    bits = ""

    for i in range(h):
        for j in range(w):
            if i % 2 != 0 or j % 2 != 0:
                bits += f"{img[i, j] & ((1 << k) - 1):0{k}b}"
                if len(bits) >= length * 8:
                    return bitstring_to_text(bits[:length * 8])
    return bitstring_to_text(bits[:length * 8])

from PIL import Image

if __name__ == "__main__":
  # Загрузка изображения
  img = Image.open("1.bmp")

  # Сообщение для внедрения
  secret = "Hello world!"

  # Встраивание
  stego = embed_message(img, secret, k=2)
  stego.save("stego.bmp")

  # Извлечение
  extracted = extract_message(Image.open("stego.bmp"), length=len(secret), k=2)
  print("Извлечено:", extracted)
