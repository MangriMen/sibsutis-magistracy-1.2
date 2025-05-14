import argparse
import os
from pathlib import Path
import sys
from PIL import Image
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import lsb
import utils.stego as stego


def main():
    parser = argparse.ArgumentParser(description="LSB Stenography for 8-bit BMP images")
    subparsers = parser.add_subparsers(dest="command", required=True)

    enc = subparsers.add_parser("encode", help="Encode message into image")
    enc.add_argument("-m", "--message", required=True, help="Message file")
    enc.add_argument("-i", "--input", required=True, help="Input BMP image")
    enc.add_argument("-o", "--output", required=True, help="Output stego image")

    dec = subparsers.add_parser("decode", help="Decode message from image")
    dec.add_argument("-i", "--input", required=True, help="Input BMP image")
    dec.add_argument("-o", "--output", required=True, help="Output message file")

    args = parser.parse_args()

    if args.command == "encode":
        encode_cmd(args)
    elif args.command == "decode":
        decode_cmd(args)


def encode_cmd(args):
    image = load_image(args.input)
    message = open(args.message, "rb").read()

    image_array = np.array(image)
    capacity = len(image_array.flatten()) // lsb.BITS_PER_BYTE

    if len(message) > capacity:
        raise ValueError(
            f"Message too large. Capacity: {capacity} bytes, message: {len(message)} bytes"
        )

    stego_array = lsb.embed_lsb_matching(image_array, image.mode, message)
    stego_img = Image.fromarray(stego_array)

    print("Embedding analysis:")
    print(f"- Capacity: {capacity} bytes")
    print(
        f"- Message size: {len(message)} bytes ({len(message) / capacity * 100:.1f}%)"
    )
    print(f"- PSNR: {stego.psnr(image_array, stego_array, image.mode):.2f} dB")

    diff_path = os.path.splitext(args.output)[0] + "_difference.bmp"
    diff_img, max_diff, attack_array = stego.generate_difference_image(
        image_array, stego_array, image
    )

    attack_img = Image.fromarray(attack_array)
    attack_img.save(diff_path + "atk.bmp")

    diff_img.save(diff_path)
    print(f"Max single pixel difference: {max_diff}")
    print(f"Difference map saved to {diff_path}")

    stego_img.save(args.output)


def decode_cmd(args):
    stego_img = load_image(args.input)
    stego_array = np.array(stego_img)

    message = lsb.extract_lsb_matching(stego_array, stego_img.mode)

    with open(args.output, "wb") as f:
        f.write(message)


def load_image(path):
    img = Image.open(path)
    if img.mode not in ("P", "L", "RGB"):
        raise ValueError(
            "Only 24-bit, 8-bit indexed or grayscale BMP images are supported."
        )
    return img


if __name__ == "__main__":
    main()
