from PIL import Image
import numpy as np
import random
from typing import Tuple, List

PADDING_PIXELS = 4  # Padding for extraction


def embed_watermark(
    image_path: str, watermark_bytes: bytes, q: float = 0.5, seed: int = 42
) -> Tuple[Image.Image, List[Tuple[int, int]]]:
    img = Image.open(image_path).convert("RGB")
    img_array = np.array(img, dtype=np.float32)
    height, width, _ = img_array.shape

    # Convert text to binary bits
    watermark_bits = _bytes_to_bits(watermark_bytes)

    watermark_length = len(watermark_bits)

    # Generate random coordinates for embedding
    pixel_coords = _generate_embedding_coordinates(
        height, width, watermark_length, seed
    )

    # Embed each bit into the image
    _embed_bits(img_array, pixel_coords, watermark_bits, q)

    # Convert back to image
    img_array = np.clip(img_array, 0, 255).astype(np.uint8)
    return Image.fromarray(img_array), pixel_coords


def _bytes_to_bits(bytes: str):
    binary_string = "".join([format(byte, "08b") for byte in bytes])
    return [int(bit) for bit in binary_string]


def _generate_embedding_coordinates(
    height: int, width: int, required_count: int, seed: int
) -> List[Tuple[int, int]]:
    random.seed(seed)
    total_pixels = (height - 2 * PADDING_PIXELS) * (width - 2 * PADDING_PIXELS)

    if required_count > total_pixels:
        raise ValueError("Watermark is too long for the image size")

    available_pixels = [
        (y, x)
        for y in range(PADDING_PIXELS, height - PADDING_PIXELS)
        for x in range(PADDING_PIXELS, width - PADDING_PIXELS)
    ]
    return random.sample(available_pixels, required_count)


def _embed_bits(
    img_array: np.ndarray, coords: List[Tuple[int, int]], bits: List[int], q: float
) -> None:
    for i, (y, x) in enumerate(coords):
        R, G, B = img_array[y, x]
        L = 0.299 * R + 0.587 * G + 0.114 * B  # Luminance
        message_bit = bits[i]

        # Modify blue channel
        img_array[y, x, 2] = B + (2 * message_bit - 1) * L * q

        # Handle overflow
        overflow_flag = 0
        if img_array[y, x, 2] > 255:
            img_array[y, x, 2] = 255
            overflow_flag = 1
        elif img_array[y, x, 2] < 0:
            img_array[y, x, 2] = 0
            overflow_flag = 1

        # Store overflow flag in LSB of green channel
        img_array[y, x, 1] = (int(G) & 0xFE) | overflow_flag


def extract_watermark(
    image_path: str, coords: List[Tuple[int, int]], c: int = 2
) -> List[int]:
    img = Image.open(image_path).convert("RGB")
    img_array = np.array(img, dtype=np.float32)
    watermark_bits = []

    for y, x in coords:
        B = img_array[y, x, 2]
        G = img_array[y, x, 1]
        overflow_flag = int(G) & 1  # Get overflow flag from LSB of green channel

        # Predict original B value
        B_pred = _predict_blue_channel(img_array, y, x, c)

        # Recover the embedded bit
        if overflow_flag == 1:
            watermark_bits.append(1 if B == 255 else 0)
        else:
            watermark_bits.append(1 if (B - B_pred) > 0 else 0)

    return watermark_bits


def _predict_blue_channel(img_array: np.ndarray, y: int, x: int, c: int) -> float:
    height, width, _ = img_array.shape
    neighbors = []

    # Collect vertical neighbors
    for k in range(-c, c + 1):
        if 0 <= y + k < height:
            neighbors.append(img_array[y + k, x, 2])

    # Collect horizontal neighbors
    for k in range(-c, c + 1):
        if 0 <= x + k < width:
            neighbors.append(img_array[y, x + k, 2])

    # Remove center pixel (added twice)
    if len(neighbors) >= 2:
        neighbors.remove(img_array[y, x, 2])
        neighbors.remove(img_array[y, x, 2])

    return (sum(neighbors) / (4 * c)) if neighbors else img_array[y, x, 2]
