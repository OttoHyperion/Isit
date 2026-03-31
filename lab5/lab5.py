import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os


class NeuralNetwork:
    """Простой многослойный персептрон с обратным распространением ошибки"""

    def __init__(self, input_size, hidden_size, output_size):
        # Инициализация весов случайными значениями
        self.weights1 = np.random.randn(input_size, hidden_size) * 0.1
        self.weights2 = np.random.randn(hidden_size, output_size) * 0.1
        self.bias1 = np.zeros((1, hidden_size))
        self.bias2 = np.zeros((1, output_size))

    def sigmoid(self, x):
        """Сигмоидальная функция активации"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    def sigmoid_derivative(self, x):
        """Производная сигмоидальной функции"""
        return x * (1 - x)

    def forward(self, X):
        """Прямой проход через сеть"""
        # Скрытый слой
        self.hidden = self.sigmoid(np.dot(X, self.weights1) + self.bias1)
        # Выходной слой
        self.output = self.sigmoid(np.dot(self.hidden, self.weights2) + self.bias2)
        return self.output

    def backward(self, X, y, output, learning_rate=0.1):
        """Обратное распространение ошибки"""
        # Вычисление ошибок
        output_error = y - output
        output_delta = output_error * self.sigmoid_derivative(output)

        hidden_error = output_delta.dot(self.weights2.T)
        hidden_delta = hidden_error * self.sigmoid_derivative(self.hidden)

        # Обновление весов и смещений
        self.weights2 += self.hidden.T.dot(output_delta) * learning_rate
        self.bias2 += np.sum(output_delta, axis=0, keepdims=True) * learning_rate
        self.weights1 += X.T.dot(hidden_delta) * learning_rate
        self.bias1 += np.sum(hidden_delta, axis=0, keepdims=True) * learning_rate

    def train(self, X, y, epochs=1000, learning_rate=0.1):
        """Обучение сети"""
        for epoch in range(epochs):
            output = self.forward(X)
            self.backward(X, y, output, learning_rate)

            # Вывод ошибки каждые 100 эпох
            if epoch % 100 == 0:
                loss = np.mean(np.square(y - output))
                print(f"Эпоха {epoch}, Ошибка: {loss:.4f}")

    def predict(self, X):
        """Предсказание для входных данных"""
        output = self.forward(X)
        return output, np.argmax(output, axis=1)


class ShapeRecognizerApp:
    """Главное приложение для распознавания геометрических фигур"""

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Распознавание геометрических фигур")
        self.window.geometry("900x700")

        # Параметры сети
        self.input_size = 400  # 20x20 пикселей
        self.hidden_size = 32  # Увеличили для большего количества классов
        # 8 фигур: круг, квадрат, треугольник, полукруг, трапеция, звезда, ромб, овал
        self.output_size = 8

        # Инициализация нейросети
        self.nn = NeuralNetwork(self.input_size, self.hidden_size, self.output_size)

        # Обучающая выборка
        self.training_data = []
        self.labels = []

        # Названия фигур
        self.shape_names = [
            "Круг", "Квадрат", "Треугольник",
            "Полукруг", "Трапеция", "Звезда",
            "Ромб", "Овал"
        ]

        # Интерфейс рисования
        self.setup_ui()

        # Загрузка данных, если они существуют
        self.load_training_data()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Основные фреймы
        left_frame = tk.Frame(self.window)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        right_frame = tk.Frame(self.window)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Область рисования
        self.canvas = tk.Canvas(left_frame, width=200, height=200, bg='white')
        self.canvas.pack(pady=10)
        self.canvas.bind("<B1-Motion>", self.paint)

        # Кнопка очистки
        clear_btn = tk.Button(left_frame, text="Очистить", command=self.clear_canvas)
        clear_btn.pack(pady=5)

        # Выбор фигуры для обучения
        shape_frame = tk.LabelFrame(left_frame, text="Выбор фигуры для обучения")
        shape_frame.pack(pady=10, fill=tk.X)

        # Создаем 2 колонки для радиокнопок
        radio_frame1 = tk.Frame(shape_frame)
        radio_frame1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        radio_frame2 = tk.Frame(shape_frame)
        radio_frame2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.shape_var = tk.IntVar(value=0)

        # Первая колонка
        for i in range(4):
            tk.Radiobutton(
                radio_frame1,
                text=f"{self.shape_names[i]} ({i})",
                variable=self.shape_var,
                value=i
            ).pack(anchor=tk.W, pady=2)

        # Вторая колонка
        for i in range(4, 8):
            tk.Radiobutton(
                radio_frame2,
                text=f"{self.shape_names[i]} ({i})",
                variable=self.shape_var,
                value=i
            ).pack(anchor=tk.W, pady=2)

        # Кнопки управления обучением
        train_frame = tk.Frame(left_frame)
        train_frame.pack(pady=10)

        tk.Button(
            train_frame,
            text="Добавить в выборку",
            command=self.add_to_training,
            width=15
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            train_frame,
            text="Обучить сеть",
            command=self.train_network,
            width=15
        ).pack(side=tk.LEFT, padx=2)

        # Кнопка распознавания
        recognize_btn = tk.Button(
            left_frame,
            text="Распознать",
            command=self.recognize_shape,
            width=32
        )
        recognize_btn.pack(pady=5)

        # Подсказка по рисованию фигур
        tip_frame = tk.LabelFrame(left_frame, text="Подсказка по рисованию")
        tip_frame.pack(pady=10, fill=tk.X)

        tips = [
            "Круг: замкнутая кривая",
            "Квадрат: 4 равные стороны",
            "Треугольник: 3 стороны",
            "Полукруг: половина круга",
            "Трапеция: 4 стороны, 2 параллельны",
            "Звезда: 5 лучей",
            "Ромб: наклоненный квадрат",
            "Овал: вытянутый круг"
        ]

        for tip in tips:
            tk.Label(tip_frame, text=tip, font=('Arial', 8), justify=tk.LEFT).pack(anchor=tk.W, pady=1)

        # Список обучающей выборки
        list_frame = tk.LabelFrame(right_frame, text="Обучающая выборка")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Scrollbar для списка
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.training_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=15)
        self.training_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.training_list.yview)

        # Кнопки управления выборкой
        btn_frame = tk.Frame(right_frame)
        btn_frame.pack(pady=5)

        tk.Button(
            btn_frame,
            text="Удалить выбранное",
            command=self.delete_selected,
            width=15
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame,
            text="Очистить выборку",
            command=self.clear_training_data,
            width=15
        ).pack(side=tk.LEFT, padx=2)

        # Область вывода результатов
        result_frame = tk.LabelFrame(right_frame, text="Результаты распознавания")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.result_label = tk.Label(
            result_frame,
            text="Результат: -\n\nНарисуйте фигуру и нажмите 'Распознать'",
            font=('Arial', 11),
            justify=tk.LEFT,
            wraplength=400
        )
        self.result_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Информация о сети
        info_frame = tk.LabelFrame(right_frame, text="Информация о сети")
        info_frame.pack(fill=tk.X, pady=10)

        info_text = f"Входной слой: {self.input_size} нейронов\n"
        info_text += f"Скрытый слой: {self.hidden_size} нейронов\n"
        info_text += f"Выходной слой: {self.output_size} нейронов\n"
        info_text += f"Примеров в выборке: {len(self.training_data)}"

        self.info_label = tk.Label(info_frame, text=info_text, justify=tk.LEFT)
        self.info_label.pack(padx=5, pady=5)

    def paint(self, event):
        """Обработка рисования на canvas"""
        x1, y1 = (event.x - 3), (event.y - 3)  # Уменьшили толщину кисти
        x2, y2 = (event.x + 3), (event.y + 3)
        self.canvas.create_oval(x1, y1, x2, y2, fill='black', outline='black')

    def clear_canvas(self):
        """Очистка canvas"""
        self.canvas.delete("all")

    def get_canvas_image(self):
        """Получение изображения с canvas в виде вектора"""
        # Создаем изображение 20x20 из canvas 200x200
        img_vector = []

        for i in range(20):
            for j in range(20):
                # Проверяем, есть ли пиксель в этой области
                x1 = i * 10
                y1 = j * 10
                x2 = x1 + 10
                y2 = y1 + 10

                # Получаем цвет пикселя в центре области
                items = self.canvas.find_overlapping(x1, y1, x2, y2)
                if items:
                    img_vector.append(1.0)  # Пиксель закрашен
                else:
                    img_vector.append(0.0)  # Пиксель пустой

        return np.array(img_vector).reshape(1, -1)

    def add_to_training(self):
        """Добавление текущего рисунка в обучающую выборку"""
        img_vector = self.get_canvas_image()
        label = self.shape_var.get()

        # Проверяем, не пустое ли изображение
        if np.sum(img_vector) < 5:  # Минимум 5 закрашенных пикселей
            messagebox.showwarning("Внимание", "Изображение слишком пустое!")
            return

        # Добавляем в выборку
        self.training_data.append(img_vector.flatten().tolist())
        self.labels.append(label)

        # Обновляем список
        self.training_list.insert(
            tk.END,
            f"{self.shape_names[label]} - Пример {len(self.training_data)}"
        )

        # Обновляем информацию
        self.update_info()

        # Сохраняем данные
        self.save_training_data()

        self.clear_canvas()
        messagebox.showinfo("Успех", f"Образ '{self.shape_names[label]}' добавлен в обучающую выборку!")

    def delete_selected(self):
        """Удаление выбранного элемента из обучающей выборки"""
        selection = self.training_list.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите элемент для удаления")
            return

        index = selection[0]

        # Удаляем из списков
        del self.training_data[index]
        del self.labels[index]

        # Обновляем отображение
        self.training_list.delete(index)

        # Обновляем информацию и сохраняем
        self.update_info()
        self.save_training_data()

        messagebox.showinfo("Успех", "Элемент удален из обучающей выборки")

    def clear_training_data(self):
        """Очистка всей обучающей выборки"""
        if len(self.training_data) == 0:
            return

        if messagebox.askyesno("Подтверждение", "Очистить всю обучающую выборку?"):
            self.training_data = []
            self.labels = []
            self.training_list.delete(0, tk.END)
            self.update_info()
            self.save_training_data()
            messagebox.showinfo("Успех", "Обучающая выборка очищена")

    def update_info(self):
        """Обновление информации о сети"""
        info_text = f"Входной слой: {self.input_size} нейронов\n"
        info_text += f"Скрытый слой: {self.hidden_size} нейронов\n"
        info_text += f"Выходной слой: {self.output_size} нейронов\n"
        info_text += f"Примеров в выборке: {len(self.training_data)}"

        # Добавляем статистику по классам
        if self.labels:
            info_text += f"\n\nРаспределение по фигурам:"
            for i, name in enumerate(self.shape_names):
                count = self.labels.count(i)
                if count > 0:
                    info_text += f"\n{name}: {count}"

        self.info_label.config(text=info_text)

    def train_network(self):
        """Обучение нейронной сети"""
        if len(self.training_data) < 10:  # Минимум 10 примеров
            messagebox.showwarning(
                "Внимание",
                f"Добавьте хотя бы 10 примеров для обучения\n"
                f"Сейчас: {len(self.training_data)} примеров"
            )
            return

        # Проверяем, есть ли хотя бы по одному примеру каждого класса
        unique_labels = set(self.labels)
        if len(unique_labels) < 3:  # Хотя бы 3 разных фигуры
            messagebox.showwarning(
                "Внимание",
                f"Добавьте примеры хотя бы для 3 разных фигур\n"
                f"Сейчас: {len(unique_labels)} разных фигур"
            )
            return

        # Подготовка данных
        X = np.array(self.training_data)

        # Создание one-hot кодирования для меток
        y = np.zeros((len(self.labels), self.output_size))
        for i, label in enumerate(self.labels):
            y[i, label] = 1

        print("Начало обучения...")
        self.nn.train(X, y, epochs=800, learning_rate=0.1)  # Увеличили количество эпох
        print("Обучение завершено!")

        # Тестируем на обучающей выборке для оценки точности
        outputs, predictions = self.nn.predict(X)
        correct = np.sum(predictions == np.array(self.labels))
        accuracy = correct / len(self.labels) * 100

        messagebox.showinfo(
            "Обучение завершено",
            f"Нейронная сеть успешно обучена!\n"
            f"Точность на обучающей выборке: {accuracy:.1f}%"
        )

    def recognize_shape(self):
        """Распознавание нарисованной фигуры"""
        if len(self.training_data) == 0:
            messagebox.showwarning("Внимание", "Сначала обучите сеть на нескольких примерах")
            return

        img_vector = self.get_canvas_image()

        # Проверяем, не пустое ли изображение
        if np.sum(img_vector) < 5:
            messagebox.showwarning("Внимание", "Нарисуйте фигуру перед распознаванием!")
            return

        output, prediction = self.nn.predict(img_vector)

        confidence = output[0][prediction[0]] * 100

        result_text = f"Результат: {self.shape_names[prediction[0]]}\n"
        result_text += f"Уверенность: {confidence:.1f}%\n\n"
        result_text += "Вероятности всех фигур:\n"

        # Сортируем вероятности по убыванию
        probabilities = []
        for i, name in enumerate(self.shape_names):
            probabilities.append((output[0][i] * 100, name))

        probabilities.sort(reverse=True)

        for prob, name in probabilities:
            if prob > 1:  # Показываем только вероятности больше 1%
                result_text += f"{name}: {prob:.1f}%\n"

        self.result_label.config(text=result_text)

    def save_training_data(self):
        """Сохранение обучающей выборки в файл"""
        data = {
            'training_data': self.training_data,
            'labels': self.labels
        }

        try:
            with open('training_data.json', 'w') as f:
                json.dump(data, f)
            print(f"Данные сохранены: {len(self.training_data)} примеров")
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def load_training_data(self):
        """Загрузка обучающей выборки из файла"""
        if os.path.exists('training_data.json'):
            try:
                with open('training_data.json', 'r') as f:
                    data = json.load(f)

                self.training_data = data['training_data']
                self.labels = data['labels']

                # Обновляем список
                for i, label in enumerate(self.labels):
                    self.training_list.insert(
                        tk.END,
                        f"{self.shape_names[label]} - Пример {i + 1}"
                    )

                self.update_info()
                print(f"Загружено {len(self.training_data)} примеров")

            except Exception as e:
                print(f"Ошибка загрузки данных: {e}")
                # Если файл поврежден, создаем пустые списки
                self.training_data = []
                self.labels = []
        else:
            print("Файл training_data.json не найден. Создана новая выборка.")

    def run(self):
        """Запуск приложения"""
        self.window.mainloop()


# Запуск приложения
if __name__ == "__main__":
    app = ShapeRecognizerApp()
    app.run()