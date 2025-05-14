import math
from PIL import Image
import numpy as np


def psnr(original: np.ndarray, distorted: np.ndarray, mode: str) -> float:
    match mode:
        case "P" | "L":
            mse = mse_8bit(original, distorted)
        case "RGB":
            mse = mse_24bit(original, distorted)
        case _:
            raise ValueError(
                "Only 24-bit, 8-bit indexed or grayscale BMP images are supported."
            )

    if mse == 0:
        return float("inf")  # Images are identical

    max_pixel = 255.0
    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))

    return psnr


def generate_lsb_attack_image(
    stego_img: Image.Image,
) -> Image.Image:
    img_array = np.array(stego_img)

    if stego_img.mode == "P":
        indices = np.array(stego_img.getdata(), dtype=np.uint8).reshape(
            stego_img.size[::-1]
        )
        lsb = (indices & 1) * 255
        attack_img = Image.fromarray(lsb.astype(np.uint8), mode="L")

    elif stego_img.mode == "L":
        # Для grayscale берем LSB пикселя
        lsb = (img_array & 1) * 255
        attack_img = Image.fromarray(lsb, mode="L")

    elif stego_img.mode == "RGB":
        # Для RGB проверяем LSB каждого канала (B, G, R)
        lsb_r = img_array[:, :, 0] & 1  # Red
        lsb_g = img_array[:, :, 1] & 1  # Green
        lsb_b = img_array[:, :, 2] & 1  # Blue

        # Если хотя бы один канал содержит бит=1, пиксель белый
        lsb_combined = ((lsb_r | lsb_g | lsb_b) * 255).astype(np.uint8)
        attack_img = Image.fromarray(lsb_combined, mode="L")

    else:
        raise ValueError(f"Unsupported image mode: {stego_img.mode}")

    return attack_img


def mse_8bit(original: np.ndarray, distorted: np.ndarray) -> float:
    original_array = original.astype(np.float64)
    distorted_array = distorted.astype(np.float64)

    if original_array.shape != distorted_array.shape:
        raise ValueError("Images must be the same size")

    # Calculate MSE
    mse = np.mean((original_array - distorted_array) ** 2)

    return mse


def mse_24bit(original: np.ndarray, distorted: np.ndarray) -> float:
    original_array = original.astype(np.float64)
    distorted_array = distorted.astype(np.float64)

    if original_array.shape != distorted_array.shape:
        raise ValueError("Images must be the same size")

    # Calculate MSE for each channel and average it
    mse_r = np.mean((original_array[:, :, 0] - distorted_array[:, :, 0]) ** 2)
    mse_g = np.mean((original_array[:, :, 1] - distorted_array[:, :, 1]) ** 2)
    mse_b = np.mean((original_array[:, :, 2] - distorted_array[:, :, 2]) ** 2)
    mse = (mse_r + mse_g + mse_b) / 3

    return mse
