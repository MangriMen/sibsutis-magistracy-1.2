import argparse
import math
from pathlib import Path
import sys
import numpy as np
from PIL import Image

import rdh

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import utils.stego as stego


def main():
    parser = argparse.ArgumentParser(description="RDH Stenography for 8-bit BMP images")

    parser.add_argument("-m", "--message", required=True, help="Message file")
    parser.add_argument("-i", "--input", required=True, help="Input BMP image")
    parser.add_argument("-o", "--output", required=True, help="Output stego image")

    args = parser.parse_args()

    message = open(args.message, "r", encoding="utf-8").read()
    secret_binary = rdh.text_to_bits(message)

    input_img = Image.open(args.input).convert("L")

    full_img = np.array(input_img)
    small_img = rdh.downscale_image(full_img)
    cover_img = rdh.upscale_inp(small_img)

    stego_img, embedded_bits = rdh.embed_secret(cover_img, secret_binary)
    rdh.save_image(stego_img, args.output)

    recovered_bits = rdh.extract_secret(
        stego_img, cover_img.astype(np.uint8), embedded_bits
    )
    output_text = rdh.bits_to_text(recovered_bits)

    psnr_val = stego.psnr(cover_img, stego_img, input_img.mode)
    capacity = embedded_bits / (full_img.shape[0] * full_img.shape[1])

    print("Встраивание завершено.")
    print(f"Встроено бит: {embedded_bits}")
    print(f"Емкость (бит/пиксель): {capacity:.4f}")
    print(f"PSNR: {psnr_val:.2f} dB")
    print(f"Извлечённый текст: {output_text}")
    print(f"Совпадает: {output_text == message}")


if __name__ == "__main__":
    main()
