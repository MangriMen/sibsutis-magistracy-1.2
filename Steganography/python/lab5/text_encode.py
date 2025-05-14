def encode_binary_to_text(lines: list[str], binary_msg: str) -> list[str]:
    """Кодирует бинарное сообщение в текст"""
    encoded_lines = []
    for i, line in enumerate(lines):
        if i < len(binary_msg):
            # Добавляем пробел в конец строки, если бит равен 1
            encoded_lines.append(line.rstrip() + (" " if binary_msg[i] == "1" else ""))
        else:
            encoded_lines.append(line)
    return encoded_lines


def extract_binary_from_text(text: str) -> str:
    """Извлекает бинарное сообщение из текста"""
    lines = text.split("\n")
    binary_msg = []

    for line in lines:
        if line.endswith(" "):
            binary_msg.append("1")
        else:
            binary_msg.append("0")

    return "".join(binary_msg)
