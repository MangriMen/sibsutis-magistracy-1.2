import argparse
import struct
import os
import math
from PIL import Image
import numpy as np

BITS_PER_BYTE = 8
LSB_BITS = 1


def read_bmp_palette_image(path):
    img = Image.open(path)
    if img.mode not in ('P', 'L'):
        raise ValueError("Only 8-bit indexed or grayscale BMP images are supported.")
    return img


def image_to_index_array(img):
    return np.array(img)


def embed_message(img, message: bytes) -> Image.Image:
    img_data = np.array(img)
    flat = img_data.flatten()

    msg_len_bytes = struct.pack("<I", len(message))
    full_msg = msg_len_bytes + message

    total_bits = len(full_msg) * BITS_PER_BYTE
    if total_bits > len(flat) * LSB_BITS:
        raise ValueError("Message too large for image")

    for i in range(total_bits):
        byte_index = i // BITS_PER_BYTE
        bit_index = i % BITS_PER_BYTE
        pixel_index = i // LSB_BITS

        bit = (full_msg[byte_index] >> bit_index) & 1
        flat[pixel_index] = (flat[pixel_index] & 0xFE) | bit

    new_img_data = flat.reshape(img_data.shape)
    encoded_img = Image.fromarray(new_img_data, mode=img.mode)

    if img.mode == 'P':
        palette = img.getpalette()
        if palette is not None:
            encoded_img.putpalette(palette)

    return encoded_img


def extract_message(img) -> bytes:
    img_data = np.array(img).flatten()

    length = 0
    for i in range(32):
        bit = img_data[i] & 1
        length |= (bit << i)

    total_bits = length * BITS_PER_BYTE
    bits = [img_data[i + 32] & 1 for i in range(total_bits)]
    out = bytearray(length)

    for i, bit in enumerate(bits):
        out[i // BITS_PER_BYTE] |= (bit << (i % BITS_PER_BYTE))

    return bytes(out)


def psnr(original: np.ndarray, stego: np.ndarray) -> float:
    diff = original.astype(np.float32) - stego.astype(np.float32)
    mse = np.mean(diff ** 2)
    if mse == 0:
        return float('inf')
    return 20 * math.log10(255.0) - 10 * math.log10(mse)


def generate_difference_image(original: np.ndarray, stego: np.ndarray, base_img: Image.Image, output_path):
    diff = np.abs(original.astype(int) - stego.astype(int))
    max_diff = diff.max()
    amplified = np.clip(diff * 50, 0, 255).astype(np.uint8)

    # Выбираем подходящий режим и палитру
    if base_img.mode == 'P' and base_img.getpalette() is not None:
        diff_img = Image.fromarray(amplified, mode='P')
        diff_img.putpalette(base_img.getpalette())
    else:
        diff_img = Image.fromarray(amplified, mode='L')

    diff_img.save(output_path)
    print(f"Max single pixel difference: {max_diff}")
    print(f"Difference map saved to {output_path}")


def encode_cmd(args):
    img = read_bmp_palette_image(args.input)
    msg = open(args.message, 'rb').read()

    orig_array = image_to_index_array(img)
    capacity = len(orig_array.flatten()) // BITS_PER_BYTE

    if len(msg) > capacity:
        raise ValueError(f"Message too large. Capacity: {capacity} bytes, message: {len(msg)} bytes")

    stego_img = embed_message(img, msg)
    stego_array = image_to_index_array(stego_img)

    print("Embedding analysis:")
    print(f"- Capacity: {capacity} bytes")
    print(f"- Message size: {len(msg)} bytes ({len(msg) / capacity * 100:.1f}%)")
    print(f"- PSNR: {psnr(orig_array, stego_array):.2f} dB")

    diff_path = os.path.splitext(args.output)[0] + "_difference.bmp"
    generate_difference_image(orig_array, stego_array, img, diff_path)

    stego_img.save(args.output)
    print(f"Stego image saved to {args.output}")


def decode_cmd(args):
    img = read_bmp_palette_image(args.input)
    msg = extract_message(img)

    with open(args.output, 'wb') as f:
        f.write(msg)

    print(f"Message successfully extracted to '{args.output}'")


def main():
    parser = argparse.ArgumentParser(description="LSB Steganography for 8-bit BMP images")
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


if __name__ == "__main__":
    main()
