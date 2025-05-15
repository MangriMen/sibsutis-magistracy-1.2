BITS_PER_BYTE = 8


def str_to_bits(text, encoding="utf-8") -> str:
    return "".join(format(byte, "08b") for byte in text.encode(encoding))


def bits_to_str(bits, encoding="utf-8") -> str:
    chars = [bits[i : i + 8] for i in range(0, len(bits), 8)]
    byte_array = bytearray(int(b, 2) for b in chars if len(b) == 8)
    return byte_array.decode(encoding, errors="ignore")


def bytes_to_bits_str(bytes: bytes) -> str:
    return "".join(format(byte, "08b") for byte in bytes)


def bits_str_to_bytes(bits: str, length: int) -> bytes:
    return bytes(
        [
            int("".join(bits[i * BITS_PER_BYTE : (i + 1) * BITS_PER_BYTE]), 2)
            for i in range(length)
        ]
    )
