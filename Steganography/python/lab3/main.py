import numpy as np
from PIL import Image
import math


def load_image(path):
    img = Image.open(path).convert("L")  # 8-битное grayscale изображение
    return np.array(img)


def save_image(image_array, path):
    # Приводим значения к диапазону [0, 255] и сохраняем
    img = Image.fromarray(np.clip(image_array, 0, 255).astype(np.uint8))
    img.save(path)


def downscale_image(img):
    # Уменьшаем изображение в 2 раза по обоим измерениям
    return img[::2, ::2]


def upscale_inp(original):
    h, w = original.shape
    new_h, new_w = h * 2, w * 2
    cover = np.zeros((new_h, new_w), dtype=np.int16)  # 🛠️ используем int16

    for i in range(h):
        for j in range(w):
            oi, oj = 2 * i, 2 * j
            cover[oi, oj] = int(original[i, j])
            if oj + 1 < new_w:
                cover[oi, oj + 1] = (
                    int(original[i, j]) + int(original[i, min(j + 1, w - 1)])
                ) // 2
            if oi + 1 < new_h:
                cover[oi + 1, oj] = (
                    int(original[i, j]) + int(original[min(i + 1, h - 1), j])
                ) // 2
            if oi + 1 < new_h and oj + 1 < new_w:
                cover[oi + 1, oj + 1] = (
                    int(cover[oi, oj + 1])
                    + int(cover[oi + 1, oj])
                    + int(original[i, j])
                ) // 3

    return cover

def scale_inp(original):
    h, w = original.shape
    new_h, new_w = h * 2 - 1, w * 2 - 1  # -1 чтобы не дублировать крайние строки/столбцы
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

def center_fold(symbol, k=3):
    M = 2 ** (k - 1)
    return symbol - M


def center_unfold(folded, k=3):
    M = 2 ** (k - 1)
    return folded + M


def embed_secret(cover, secret_bits, k=3):
    h, w = cover.shape
    folded_symbols = []
    i = 0
    max_symbols = (h // 3) * (w // 3)
    # print(secret_bits)
    while i + k <= len(secret_bits) and len(folded_symbols) < max_symbols:
        # print(i, i+k)
        symbol = int(secret_bits[i : i + k], 2)
        # print(symbol)
        # exit(1)
        folded = center_fold(symbol, k)
        folded_symbols.append(folded)
        i += k

    stego = cover.copy().astype(
        np.int16
    )  # 🛠️ int16, чтобы вместить отрицательные значения
    idx = 0
    for y in range(0, h - 2, 3):
        for x in range(0, w - 2, 3):
            if idx >= len(folded_symbols):
                break
            stego[y, x + 1] += folded_symbols[idx]  # может быть отрицательное изменение
            idx += 1

    return (
        np.clip(stego, 0, 255).astype(np.uint8),
        idx * k,
    )  # 🛠️ обрезаем перед возвратом


def extract_secret(stego, cover, total_bits, k=3):
    h, w = stego.shape
    symbols = []
    idx = 0
    for y in range(0, h - 2, 3):
        for x in range(0, w - 2, 3):
            if idx * k >= total_bits:
                break
            diff = int(stego[y, x + 1]) - int(cover[y, x + 1])
            symbol = center_unfold(diff, k)
            symbol_bin = format(symbol, f"0{k}b")
            symbols.append(symbol_bin)
            idx += 1

    return "".join(symbols)


def psnr(original, stego):
    original = original.astype(np.float32)
    stego = stego.astype(np.float32)
    mse = np.mean((original - stego) ** 2)
    if mse == 0:
        return float("inf")
    return 20 * math.log10(255.0 / math.sqrt(mse))


def text_to_binary_string(text: str) -> str:
    return ''.join(f'{byte:08b}' for byte in text.encode('utf-8'))


def binary_string_to_text(binary_str: str) -> str:
    if len(binary_str) % 8 != 0:
        raise ValueError("Binary string length must be a multiple of 8")
    byte_list = [int(binary_str[i:i+8], 2) for i in range(0, len(binary_str), 8)]
    return bytes(byte_list).decode('utf-8')

# === MAIN TEST ===
if __name__ == "__main__":
    input_image_path = "1.bmp"  # Замените на свой файл
    output_image_path = "stego.bmp"

    message = "Hello world"

    secret_binary = text_to_binary_string("1")
    # secret_binary = "011010101100111000101" * 100
    # print(secret_binary)
    # print(len(secret_binary))

    # 1. Загрузка и уменьшение
    full_img = load_image(input_image_path)
    small_img = downscale_image(full_img)

    # 2. Интерполяция
    cover_img = scale_inp(small_img)

    # 3. Встраивание
    stego_img, embedded_bits = embed_secret(cover_img, secret_binary)

    # 4. Сохранение
    save_image(stego_img, output_image_path)

    # 5. Извлечение и проверка
    recovered_secret = extract_secret(
        stego_img, cover_img.astype(np.uint8), embedded_bits
    )

    # 6. Метрики
    psnr_val = psnr(cover_img.astype(np.uint8), stego_img)
    capacity = embedded_bits / (full_img.shape[0] * full_img.shape[1])

    print("✅ Встраивание завершено.")
    print(f"Встроено бит: {embedded_bits}")
    print(f"Емкость (бит/пиксель): {capacity:.4f}")
    print(f"PSNR: {psnr_val:.2f} dB")
    print(
        f"Извлеченные данные совпадают: {recovered_secret == secret_binary[:embedded_bits]}"
    )
    print(recovered_secret)

    # print(binary_string_to_text(recovered_secret))
