def str_to_bits(text, encoding="utf-8") -> str:
    return "".join(format(byte, "08b") for byte in text.encode(encoding))


def bits_to_str(bits, encoding="utf-8") -> str:
    chars = [bits[i : i + 8] for i in range(0, len(bits), 8)]
    byte_array = bytearray(int(b, 2) for b in chars if len(b) == 8)
    return byte_array.decode(encoding, errors="ignore")
