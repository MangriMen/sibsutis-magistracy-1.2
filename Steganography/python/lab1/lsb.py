from PIL import Image
import numpy as np

BITS_PER_BYTE = 8
BYTE_ORDER = "big"
MESSAGE_LENGTH_BYTES = 4


def embed_lsb_matching(
    image_array: np.ndarray, mode: str, message_bytes: bytes
) -> Image.Image:
    match mode:
        case "P" | "L":
            return embed_lsb_matching_8bit(image_array, message_bytes)
        case "RGB":
            return embed_lsb_matching_24bit(image_array, message_bytes)
        case _:
            raise ValueError(
                "Only 24-bit, 8-bit indexed or grayscale BMP images are supported."
            )


def extract_lsb_matching(stego_array: np.ndarray, mode: str) -> Image.Image:
    match mode:
        case "P" | "L":
            return extract_lsb_matching_8bit(stego_array)
        case "RGB":
            return extract_lsb_matching_24bit(stego_array)
        case _:
            raise ValueError(
                "Only 24-bit, 8-bit indexed or grayscale BMP images are supported."
            )


def prepare_for_lsb(image_array: np.ndarray, message_bytes: bytes):
    if not isinstance(message_bytes, bytes):
        raise ValueError("Message must be bytes")

    # Add the message length (4 bytes) to the beginning
    message_length = len(message_bytes)
    length_bytes = message_length.to_bytes(MESSAGE_LENGTH_BYTES, byteorder=BYTE_ORDER)
    full_message = length_bytes + message_bytes
    message_bits = "".join([format(byte, "08b") for byte in full_message])

    # Check capacity
    total_pixels = image_array.size
    required_pixels = len(message_bits)
    if required_pixels > total_pixels:
        raise ValueError("The message is too big to fit in the image")

    return message_bits


def embed_lsb_matching_8bit(
    image_array: np.ndarray, message_bytes: bytes
) -> np.ndarray:
    message_bits = prepare_for_lsb(image_array, message_bytes)

    image_array = image_array.copy()
    flat_array = image_array.flatten()
    for i in range(len(message_bits)):
        message_bit = int(message_bits[i])

        if (flat_array[i] & 1) != message_bit:
            # Randomly change LSB if bits are not equal
            if flat_array[i] == 255:
                flat_array[i] -= 1
            elif flat_array[i] == 0:
                flat_array[i] += 1
            else:
                flat_array[i] += np.random.choice([-1, 1])

    # Reshape embedded image in 2d
    embedded_array = flat_array.reshape(image_array.shape)

    return embedded_array


def embed_lsb_matching_24bit(
    image_array: np.ndarray, message_bytes: bytes
) -> np.ndarray:
    message_bits = prepare_for_lsb(image_array, message_bytes)

    image_array = image_array.copy()

    bit_index = 0
    for row in image_array:
        for pixel in row:
            for channel in range(3):  # B, G, R
                if bit_index >= len(message_bits):
                    break
                bit = int(message_bits[bit_index])
                if (pixel[channel] & 1) != bit:
                    # Randomly change LSB if bits are not equal
                    if pixel[channel] == 255:
                        pixel[channel] -= 1
                    elif pixel[channel] == 0:
                        pixel[channel] += 1
                    else:
                        pixel[channel] += np.random.choice([-1, 1])
                bit_index += 1

    return image_array


def extract_lsb_matching_8bit(image_array: np.ndarray) -> bytes:
    image_array = image_array.copy()
    flat_img = image_array.flatten()

    length_bits_count = MESSAGE_LENGTH_BYTES * BITS_PER_BYTE

    # Extract message length (first 32 bits)
    length_bits = [str(pixel & 1) for pixel in flat_img[:length_bits_count]]
    length = int("".join(length_bits), 2)

    # Extract message
    message_bits = []
    for i in range(length_bits_count, length_bits_count + length * BITS_PER_BYTE):
        message_bits.append(str(flat_img[i] & 1))

    # Convert message bits to bytes
    return bits_str_to_bytes(message_bits, length)


def extract_lsb_matching_24bit(image_array: np.ndarray):
    image_array = image_array.copy()

    length_bits_count = MESSAGE_LENGTH_BYTES * BITS_PER_BYTE

    # Extract message length (first 32 bits)
    length_bits = []
    bit_count = 0
    for row in image_array:
        for pixel in row:
            for channel in range(3):
                if bit_count >= length_bits_count:
                    break
                length_bits.append(str(pixel[channel] & 1))
                bit_count += 1

    length = int("".join(length_bits), 2)

    # Extract message
    message_bits = []
    total_bits = length_bits_count + length * BITS_PER_BYTE
    bit_count = 0
    for row in image_array:
        for pixel in row:
            for channel in range(3):
                if bit_count >= total_bits:
                    break
                if bit_count >= length_bits_count:  # Skip length
                    message_bits.append(str(pixel[channel] & 1))
                bit_count += 1

    # Convert message bits to bytes
    return bits_str_to_bytes(message_bits, length)


def bits_str_to_bytes(bits: str, length: int) -> bytes:
    return bytes(
        [
            int("".join(bits[i * BITS_PER_BYTE : (i + 1) * BITS_PER_BYTE]), 2)
            for i in range(length)
        ]
    )
