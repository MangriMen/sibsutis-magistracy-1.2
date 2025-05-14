from pathlib import Path
import sys
import numpy as np
from PIL import Image

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from utils import stego, string


def load_image(path):
    img = Image.open(path).convert("L")
    return np.array(img)


def save_image(image_array, path):
    img = Image.fromarray(np.clip(image_array, 0, 255).astype(np.uint8))
    img.save(path)


def downscale_image(img):
    return img[::2, ::2]


def upscale_inp(original):
    h, w = original.shape
    new_h, new_w = h * 2 - 1, w * 2 - 1
    result = np.zeros((new_h, new_w), dtype=np.uint8)

    for i in range(h):
        for j in range(w):
            result[2 * i, 2 * j] = original[i, j]

    for i in range(0, new_h, 2):
        for j in range(1, new_w, 2):
            left = result[i, j - 1]
            right = result[i, j + 1] if j + 1 < new_w else left
            result[i, j] = (int(left) + int(right)) // 2

    for i in range(1, new_h, 2):
        for j in range(0, new_w, 2):
            top = result[i - 1, j]
            bottom = result[i + 1, j] if i + 1 < new_h else top
            result[i, j] = (int(top) + int(bottom)) // 2

    for i in range(1, new_h, 2):
        for j in range(1, new_w, 2):
            tl = result[i - 1, j - 1]
            tr = result[i - 1, j + 1] if j + 1 < new_w else tl
            bl = result[i + 1, j - 1] if i + 1 < new_h else tl
            br = result[i + 1, j + 1] if (i + 1 < new_h and j + 1 < new_w) else tl
            result[i, j] = (int(tl) + int(tr) + int(bl) + int(br)) // 4

    return result


def center_fold(d, k):
    M = 2 ** (k - 1)
    return d - M


def center_unfold(folded, k):
    M = 2 ** (k - 1)
    return folded + M


def get_code_and_index(d):
    folded = center_fold(d, 3)
    if -2 <= folded <= 1:
        return 0, folded
    else:
        return 1, folded - 4


def get_symbol_from_code(index, code):
    if index == 0:
        return center_unfold(code, 3)
    else:
        return center_unfold(code + 4, 3)


def embed_secret(cover, secret_bits, k=1):
    h, w = cover.shape
    stego = cover.copy().astype(np.int16)
    i = 0
    embedded_bits = 0

    for y in range(0, h - 2, 3):
        for x in range(0, w - 2, 3):
            if i + 4 * k > len(secret_bits):
                return np.clip(stego, 0, 255).astype(np.uint8), embedded_bits

            symbols = [
                int(secret_bits[i + j * k : i + (j + 1) * k], 2) for j in range(4)
            ]
            i += 4 * k
            embedded_bits += 4 * k

            codes = []
            indexes = []
            for s in symbols:
                index, code = get_code_and_index(s)
                codes.append(code)
                indexes.append(index)

            index_bin = "".join(map(str, indexes))
            I = int(index_bin, 2)
            M = 2**k
            Pc = int(cover[y + 2, x + 2])
            stego[y + 2, x + 2] = Pc + (I - M)

            positions = [(y, x + 1), (y + 1, x), (y + 1, x + 2), (y + 2, x + 1)]
            for pos, code in zip(positions, codes):
                stego[pos] += code

    return np.clip(stego, 0, 255).astype(np.uint8), embedded_bits


def extract_secret(stego, cover, total_bits, k=1):
    h, w = stego.shape
    recovered_bits = []
    bits_per_block = 4 * k
    count = 0

    for y in range(0, h - 2, 3):
        for x in range(0, w - 2, 3):
            if count + bits_per_block > total_bits:
                return "".join(recovered_bits)

            positions = [(y, x + 1), (y + 1, x), (y + 1, x + 2), (y + 2, x + 1)]
            codes = [int(stego[pos]) - int(cover[pos]) for pos in positions]

            Pc = int(cover[y + 2, x + 2])
            Pc_ = int(stego[y + 2, x + 2])
            I = Pc_ - Pc + 2**k
            index_bin = format(I, f"0{4}b")
            indexes = list(map(int, index_bin))

            for idx, code in zip(indexes, codes):
                s = get_symbol_from_code(idx, code)
                print(format(s, f"0{k}b"))
                recovered_bits.append(format(s, f"0{k}b"))
            count += bits_per_block

    return "".join(recovered_bits)


def main():
    input_image_path = "../../images/1.bmp"
    output_image_path = "stego.bmp"

    input_text = "Lorem ipsum dolor sit amet consectetur adipiscing elit"
    secret_binary = string.str_to_bits(input_text)

    img = Image.open(input_image_path).convert("L")

    full_img = load_image(input_image_path)
    small_img = downscale_image(full_img)
    cover_img = upscale_inp(small_img)

    stego_img, embedded_bits = embed_secret(cover_img, secret_binary)
    save_image(stego_img, output_image_path)

    recovered_bits = extract_secret(
        stego_img, cover_img.astype(np.uint8), embedded_bits
    )
    print(recovered_bits)
    output_text = string.bits_to_str(recovered_bits)

    psnr_val = stego.psnr(cover_img.astype(np.uint8), stego_img, img.mode)
    capacity = embedded_bits / (full_img.shape[0] * full_img.shape[1])

    print("Встраивание завершено.")
    print(f"Встроено бит: {embedded_bits}")
    print(f"Емкость (бит/пиксель): {capacity:.4f}")
    print(f"PSNR: {psnr_val:.2f} dB")
    print(f"Извлечённый текст: {output_text}")
    print(f"Совпадает: {output_text == input_text}")


if __name__ == "__main__":
    main()
