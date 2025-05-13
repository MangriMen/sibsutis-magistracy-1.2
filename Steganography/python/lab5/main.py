import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import urllib.request
import random
from tkinter import simpledialog


class Steganography5:
    def __init__(self, root):
        self.root = root
        self.root.title("Текстовая стеганография")
        self.root.geometry("900x800")

        self.source_text = ""
        self.hidden_message = ""
        self.encoded_text = ""

        self.create_widgets()

    def paste_from_clipboard(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.encoded_text_area.delete(1.0, tk.END)
            self.encoded_text_area.insert(tk.END, clipboard_text)
        except tk.TclError:
            messagebox.showwarning(
                "Предупреждение", "Буфер обмена пуст или содержит не текстовые данные"
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось вставить текст: {str(e)}")

    def create_widgets(self):
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10), padding=6)
        self.tab_control = ttk.Notebook(self.root)

        self.tab_encode = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_encode, text="Кодирование")

        self.tab_decode = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_decode, text="Декодирование")

        self.tab_control.pack(expand=1, fill="both")

        # Кодирование
        ttk.Label(self.tab_encode, text="Исходный текст:").pack(pady=(10, 0))
        self.source_text_area = scrolledtext.ScrolledText(
            self.tab_encode, height=15, wrap=tk.WORD, font=("Arial", 10)
        )
        self.source_text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        load_frame = ttk.Frame(self.tab_encode)
        load_frame.pack(fill=tk.X, padx=10, pady=5)

        self.load_gutenberg_btn = ttk.Button(
            load_frame, text="Загрузить из Gutenberg", command=self.load_from_gutenberg
        )
        self.load_gutenberg_btn.pack(side=tk.LEFT, padx=5)

        self.load_file_btn = ttk.Button(
            load_frame, text="Загрузить файл", command=self.load_from_file
        )
        self.load_file_btn.pack(side=tk.LEFT, padx=5)

        ttk.Label(self.tab_encode, text="Сообщение для скрытия:").pack()
        self.message_entry = ttk.Entry(self.tab_encode)
        self.message_entry.pack(fill=tk.X, padx=10, pady=5)

        self.encode_btn = ttk.Button(
            self.tab_encode, text="Закодировать сообщение", command=self.encode_message
        )
        self.encode_btn.pack(pady=5)

        ttk.Label(self.tab_encode, text="Результат:").pack()
        self.result_text_area = scrolledtext.ScrolledText(
            self.tab_encode, height=15, wrap=tk.WORD, font=("Arial", 10)
        )
        self.result_text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        result_btn_frame = ttk.Frame(self.tab_encode)
        result_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.copy_result_btn = ttk.Button(
            result_btn_frame, text="Копировать результат", command=self.copy_result
        )
        self.copy_result_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.save_result_btn = ttk.Button(
            result_btn_frame, text="Сохранить результат", command=self.save_result
        )
        self.save_result_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Декодирование
        decode_btn_frame = ttk.Frame(self.tab_decode)
        decode_btn_frame.pack(fill=tk.X, padx=10, pady=5)

        self.load_encoded_btn = ttk.Button(
            decode_btn_frame, text="Загрузить файл", command=self.load_encoded_file
        )
        self.load_encoded_btn.pack(side=tk.LEFT, padx=5)

        self.paste_btn = ttk.Button(
            decode_btn_frame, text="Вставить", command=self.paste_from_clipboard
        )
        self.paste_btn.pack(side=tk.LEFT, padx=5)
        decode_load_frame = ttk.Frame(self.tab_decode)
        decode_load_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(self.tab_decode, text="Текст со скрытым сообщением:").pack()
        self.encoded_text_area = scrolledtext.ScrolledText(
            self.tab_decode, height=15, wrap=tk.WORD, font=("Arial", 10)
        )
        self.encoded_text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.decode_btn = ttk.Button(
            self.tab_decode, text="Декодировать сообщение", command=self.decode_message
        )
        self.decode_btn.pack(pady=5)

        ttk.Label(self.tab_decode, text="Извлеченное сообщение:").pack()
        self.decoded_message_entry = ttk.Entry(self.tab_decode)
        self.decoded_message_entry.pack(fill=tk.X, padx=10, pady=5)

    def copy_result(self):
        result_text = self.result_text_area.get(1.0, tk.END)
        if result_text.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(result_text)
            messagebox.showinfo("Успех", "Текст скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Предупреждение", "Нет текста для копирования")

    def load_from_gutenberg(self):
        try:
            books = [
                "https://dev.gutenberg.org/files/1342/1342-0.txt",  # Pride and Prejudice
                "https://dev.gutenberg.org/files/11/11-0.txt",  # Alice's Adventures in Wonderland
                "https://dev.gutenberg.org/files/2701/2701-0.txt",  # Moby Dick
                "https://dev.gutenberg.org/files/84/84-0.txt",  # Frankenstein
                "https://dev.gutenberg.org/files/98/98-0.txt",  # A Tale of Two Cities
            ]

            url = random.choice(books)
            self.source_text_area.delete(1.0, tk.END)
            self.source_text_area.insert(tk.END, "Идет загрузка текста...")
            self.root.update()

            with urllib.request.urlopen(url) as response:
                text = response.read().decode("utf-8")
                lines = text.split("\n")
                self.source_text = "\n".join(lines[:2000])  # Берем первые строки
                self.source_text_area.delete(1.0, tk.END)
                self.source_text_area.insert(tk.END, self.source_text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить текст: {str(e)}")

    def load_from_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.source_text = f.read()
                self.source_text_area.delete(1.0, tk.END)
                self.source_text_area.insert(tk.END, self.source_text)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def load_encoded_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.encoded_text = f.read()
                self.encoded_text_area.delete(1.0, tk.END)
                self.encoded_text_area.insert(tk.END, self.encoded_text)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def encode_message(self):
        message = self.message_entry.get()
        if not message:
            messagebox.showwarning("Предупреждение", "Введите сообщение для скрытия")
            return

        if not self.source_text_area.get(1.0, tk.END).strip():
            messagebox.showwarning("Предупреждение", "Загрузите исходный текст")
            return

        self.source_text = self.source_text_area.get(1.0, tk.END)
        try:
            binary_msg = "".join(
                format(byte, "08b") for byte in message.encode("utf-8")
            )

            lines = self.source_text.split("\n")
            required_lines = len(message.encode("utf-8")) * 8
            if len(lines) < required_lines:
                messagebox.showerror(
                    "Ошибка", f"Текст слишком короткий для этого сообщения."
                )
                return

            encoded_lines = []
            for i, line in enumerate(lines):
                if i < len(binary_msg):
                    if binary_msg[i] == "1":
                        encoded_lines.append(line.rstrip() + " ")
                    else:
                        encoded_lines.append(line.rstrip())
                else:
                    encoded_lines.append(line)

            self.encoded_text = "\n".join(encoded_lines)
            self.result_text_area.delete(1.0, tk.END)
            self.result_text_area.insert(tk.END, self.encoded_text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при кодировании: {str(e)}")

    def decode_message(self):
        encoded_text = self.encoded_text_area.get(1.0, tk.END)
        if not encoded_text.strip():
            messagebox.showwarning(
                "Предупреждение", "Загрузите текст со скрытым сообщением"
            )
            return

        try:
            lines = encoded_text.split("\n")
            binary_msg = []

            for line in lines:
                if line.endswith(" "):
                    binary_msg.append("1")
                else:
                    binary_msg.append("0")

            binary_str = "".join(binary_msg)
            message_bytes = bytes(
                [
                    int(binary_str[i : i + 8], 2)
                    for i in range(0, len(binary_str), 8)
                    if binary_str[i : i + 8] != "00000000"
                ]
            )
            message = message_bytes.decode("utf-8")

            self.decoded_message_entry.delete(0, tk.END)
            self.decoded_message_entry.insert(0, message)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при декодировании: {str(e)}")

    def save_result(self):
        if not self.result_text_area.get(1.0, tk.END).strip():
            messagebox.showwarning("Предупреждение", "Нет данных для сохранения")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.result_text_area.get(1.0, tk.END))
                messagebox.showinfo("Успех", "Файл успешно сохранен")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")


root = tk.Tk()
app = Steganography5(root)
root.mainloop()
