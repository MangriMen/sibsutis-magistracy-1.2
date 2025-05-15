import numpy as np
from PIL import Image


def text_to_bits(text, encoding="utf-8") -> str:
    return "".join(format(byte, "08b") for byte in text.encode(encoding))


def bits_to_text(bits, encoding="utf-8") -> str:
    chars = [bits[i : i + 8] for i in range(0, len(bits), 8)]
    byte_array = bytearray(int(b, 2) for b in chars if len(b) == 8)
    return byte_array.decode(encoding, errors="ignore")


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


def get_code_and_index(d, k):
    M = 2 ** (k - 1)
    if d < M:
        return 0, d - M  # center
    else:
        return 1, d - M - (2 ** (k - 1))  # shifted for index 1


def get_symbol_from_code(index, code, k):
    M = 2 ** (k - 1)
    if index == 0:
        return code + M
    else:
        return code + M + (2 ** (k - 1))


def embed_secret(cover, secret_bits, k=4):
    h, w = cover.shape
    stego = cover.copy().astype(np.int16)
    i = 0
    embedded_bits = 0

    for y in range(0, h - 2, 4):
        for x in range(0, w - 2, 4):
            if i + 4 * k > len(secret_bits):
                return np.clip(stego, 0, 255).astype(np.uint8), embedded_bits

            symbols = []
            for j in range(4):
                start = i + j * k
                end = i + (j + 1) * k
                if end > len(secret_bits):
                    bits = secret_bits[start:] + "0" * (end - len(secret_bits))
                    symbols.append(int(bits, 2))
                    embedded_bits += len(secret_bits[start:])
                    i = len(secret_bits)
                    break
                else:
                    bits = secret_bits[start:end]
                    symbols.append(int(bits, 2))
                    embedded_bits += k
            else:
                i += 4 * k

            codes = []
            indexes = []
            for s in symbols:
                index, code = get_code_and_index(s, k)
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


def extract_secret(stego, cover, total_bits, k=4):
    h, w = stego.shape
    recovered_bits = []
    count = 0

    for y in range(0, h - 2, 4):
        for x in range(0, w - 2, 4):
            if count >= total_bits:
                break

            positions = [(y, x + 1), (y + 1, x), (y + 1, x + 2), (y + 2, x + 1)]
            codes = [int(stego[pos]) - int(cover[pos]) for pos in positions]

            Pc = int(cover[y + 2, x + 2])
            Pc_ = int(stego[y + 2, x + 2])
            I = Pc_ - Pc + 2**k
            I = max(0, min(15, I))
            index_bin = format(I, f"0{4}b")[-4:]
            indexes = list(map(int, index_bin))

            for idx, code in zip(indexes, codes):
                if count >= total_bits:
                    break
                s = get_symbol_from_code(idx, code, k)
                s = max(0, min(2**k - 1, s))
                recovered_bits.append(format(s, f"0{k}b"))
                count += k

    return "".join(recovered_bits)[:total_bits]
