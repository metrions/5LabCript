import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
from collections import Counter
import math

# Функция для генерации последовательности с помощью LFSR
def lfsr(seed, polynomial, length):

    # Преобразуем сид и полином в списки чисел
    liSeed = [int(x) for x in seed]
    poly = [int(x) for x in polynomial]
    
    sequence = []  # Итоговая последовательность

    for _ in range(length):
        # Сохраняем младший бит в последовательность
        sequence.append(liSeed[-1])
        
        # Вычисляем обратную связь (XOR битов, где полином равен 1)
        feedback = 0
        for i in range(len(liSeed)):
            if poly[i] == 1:
                feedback ^= liSeed[i]
        
        # Сдвиг регистра вправо, новый бит записывается в старший разряд
        liSeed = [feedback] + liSeed[:-1]

    return sequence


# Функция SG-генератора (комбинирование LFSR)
def sg_generator(g1, g2):
    g1 = [x for x in g1]
    g2 = [x for x in g2]
    sg_sequence = [a if s == 1 else None for a, s in zip(g1, g2)]
    return [x for x in sg_sequence if x is not None]

# Расчет критерия χ²-Пирсона
def chi_squared_test(sequence, alphabet_size):
    counts = Counter(sequence)
    expected = len(sequence) / alphabet_size
    chi_squared = sum((count - expected)**2 / expected for count in counts.values())
    return chi_squared, len(counts) - 1  # Возвращаем значение χ² и число степеней свободы

DictCrit = {1: 3.84,
            2: 5.99,
            3: 7.82,
            4: 9.49,
            5: 11.07,
            6: 12.59,
            7: 14.07,
            8: 15.51,
            9: 16.92,
            10: 18.31,
            11: 19.68,
            12: 21.03,
            13: 22.36,
            14: 23.69,
            15: 25,
            16: 26.3
            }

# Расчёт критического значения
def crit(r):
    if r > 16: r = 16
    return DictCrit[r]

# Основное приложение с графическим интерфейсом
class GeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор последовательностей")

        # Поля для ввода параметров
        self.polynomial_g1 = tk.StringVar()
        self.seed_g1 = tk.StringVar()
        self.polynomial_g2 = tk.StringVar()
        self.seed_g2 = tk.StringVar()
        self.sequence_length = tk.StringVar(value="10")

        # Результаты
        self.result_sequence = None

        # Интерфейс
        self.create_widgets()

    def import_data(self):
        # Открыть диалог выбора файла
        file_path = filedialog.askopenfilename(
            title="Выберите файл с параметрами",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if not file_path:
            return  # Если файл не выбран, ничего не делать

        try:
            # Читаем данные из файла
            with open(file_path, "r") as file:
                lines = file.readlines()

            # Проверяем количество строк в файле
            if len(lines) < 5:
                messagebox.showerror("Ошибка", "Файл должен содержать 5 строк с параметрами!")
                return

            # Устанавливаем значения в поля
            self.polynomial_g1.set(lines[0].strip())
            self.seed_g1.set(lines[1].strip())
            self.polynomial_g2.set(lines[2].strip())
            self.seed_g2.set(lines[3].strip())
            self.sequence_length.set(lines[4].strip())

            messagebox.showinfo("Успех", "Данные успешно импортированы!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")

    def export_data(self):
        # Открыть диалог для выбора места сохранения файла
        file_path = filedialog.asksaveasfilename(
            title="Сохранить параметры в файл",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if not file_path:
            return  # Если пользователь закрыл диалог без сохранения

        try:
            # Собираем параметры для сохранения
            data_to_save = [
                f"Полином G1: {self.polynomial_g1.get()}",
                f"Сид G1: {self.seed_g1.get()}",
                f"Полином G2: {self.polynomial_g2.get()}",
                f"Сид G2: {self.seed_g2.get()}",
                f"Длина последовательности: {self.sequence_length.get()}"
            ]

            # Записываем данные в файл
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(data_to_save))
                file.write("\n\nРезультаты генерации:\n")
                file.write(self.result_text.get(1.0, tk.END))

            messagebox.showinfo("Успех", f"Данные успешно сохранены в файл: {file_path}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def create_widgets(self):
        # Ввод параметров генераторов
        params_frame = ttk.LabelFrame(self.root, text="Параметры генераторов")
        params_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(params_frame, text="Полином G1:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(params_frame, textvariable=self.polynomial_g1).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(params_frame, text="Сид G1:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(params_frame, textvariable=self.seed_g1).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(params_frame, text="Полином G2:").grid(row=2, column=0, padx=5, pady=5)
        ttk.Entry(params_frame, textvariable=self.polynomial_g2).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(params_frame, text="Сид G2:").grid(row=3, column=0, padx=5, pady=5)
        ttk.Entry(params_frame, textvariable=self.seed_g2).grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(params_frame, text="Длина последовательности:").grid(row=4, column=0, padx=5, pady=5)
        ttk.Entry(params_frame, textvariable=self.sequence_length).grid(row=4, column=1, padx=5, pady=5)

        # Кнопки
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.grid(row=1, column=0, padx=10, pady=10)

        ttk.Button(buttons_frame, text="Сгенерировать", command=self.generate_sequence).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(buttons_frame, text="Импортировать данные", command=self.import_data).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(buttons_frame, text="Выход", command=self.root.quit).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(buttons_frame, text="Экспортировать данные", command=self.export_data).grid(row=0, column=2, padx=5, pady=5)


        # Поле для отображения результатов
        self.result_text = tk.Text(self.root, height=15, width=80)
        self.result_text.grid(row=2, column=0, padx=10, pady=10)

    def generate_sequence(self):
        # Получаем параметры
        poly_g1 = str(self.polynomial_g1.get())
        seed_g1 = str(self.seed_g1.get())
        poly_g2 = str(self.polynomial_g2.get())
        seed_g2 = str(self.seed_g2.get())
        length = int(self.sequence_length.get())
        # Генерируем последовательности
        g1 = lfsr(seed_g1, poly_g1, length)
        g2 = lfsr(seed_g2, poly_g2, length)

        # SG-генератор
        sg_sequence = sg_generator(g1, g2)

        # Расчет периода
        period = (2 ** len(seed_g1) - 1) * (2 ** (len(seed_g2) - 1))

        # Проверка критерия χ²-Пирсона
        alphabet_size = 2  # В нашем случае алфавит {0, 1}
        chi_squared, degrees_of_freedom = chi_squared_test(sg_sequence, alphabet_size)

        # Табличное значение χ² для проверки
        critical_value = crit(len(sg_sequence) - 1)

        # Вывод результатов
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Сгенерированная последовательность: {sg_sequence}\n")
        self.result_text.insert(tk.END, f"Период последовательности: {period}\n")
        self.result_text.insert(tk.END, f"Значение χ²: {chi_squared:.2f}\n")
        self.result_text.insert(tk.END, f"Критическое значение χ²: {critical_value}\n")
        self.result_text.insert(tk.END, f"Результат проверки: {'Соответствует равномерному распределению' if chi_squared < critical_value else 'Не соответствует равномерному распределению'}\n")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = GeneratorApp(root)
    root.mainloop()
