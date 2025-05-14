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


def generate_difference_image(
    original: np.ndarray,
    stego: np.ndarray,
    base_img: Image.Image,
    amplification_factor: int = 50,
) -> tuple[Image.Image, int]:
    # Check sizes
    if original.shape != stego.shape:
        raise ValueError("Images must be the same size")

    diff = np.abs(original.astype(int) - stego.astype(int))
    max_diff = diff.max()

    # Amplify difference and clip to pixel range
    amplified = np.clip(diff * amplification_factor, 0, 255).astype(np.uint8)

    if base_img.mode == "P" and base_img.getpalette() is not None:
        # 8-bit with palette
        diff_img = Image.fromarray(amplified, mode="P")
        diff_img.putpalette(base_img.getpalette())
    elif base_img.mode == "L":
        # 8-bit grayscale
        diff_img = Image.fromarray(amplified, mode="L")
    elif base_img.mode == "RGB":
        # 24-bit diff per channel
        if len(original.shape) == 3 and original.shape[2] == 3:
            # Combine RGB channels
            combined_diff = np.sum(amplified, axis=2) // 3
            diff_img = Image.fromarray(combined_diff.astype(np.uint8), mode="L")
        else:
            raise ValueError("Image must be 24-bit in this case")
    else:
        raise ValueError(f"Unsupported bmp mode: {base_img.mode}")

    attack_img = stego.copy().flatten()

    for i in range(len(attack_img)):
        if (attack_img[i] & 1) == 0:
            attack_img[i] = 0
        elif (attack_img[i] & 1) == 1:
            attack_img[i] = 255

    return diff_img, max_diff, attack_img


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
