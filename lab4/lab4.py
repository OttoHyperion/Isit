import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Candidate:
    """Класс для представления кандидата"""

    def __init__(self, id: int, name: str, description: str = ""):
        self.id = id
        self.name = name
        self.description = description
        self.scores = {}  # оценки по критериям

    def __str__(self):
        return f"{self.name}"


class VoteSystem:
    """Система голосования"""

    def __init__(self):
        self.candidates = []
        self.votes = []  # список бюллетеней
        self.criteria = ["Успеваемость", "Организаторские", "Коммуникабельность", "Ответственность"]

    def add_candidate(self, name: str, description: str = ""):
        candidate_id = len(self.candidates)
        candidate = Candidate(candidate_id, name, description)
        self.candidates.append(candidate)
        return candidate

    def add_vote(self, preferences: List[int]):
        """Добавление бюллетеня с предпочтениями"""
        if len(preferences) != len(self.candidates):
            raise ValueError("Неверное количество кандидатов в бюллетене")
        self.votes.append(preferences)

    def plurality(self) -> Dict:
        """Метод относительного большинства"""
        if not self.votes:
            return {"winner": None, "scores": {}, "explanation": "Нет голосов"}

        # Подсчитываем голоса за первых предпочтений
        scores = {candidate.id: 0 for candidate in self.candidates}
        for vote in self.votes:
            first_pref = vote[0]
            scores[first_pref] += 1

        # Находим победителя
        max_score = max(scores.values())
        winners = [cid for cid, score in scores.items() if score == max_score]

        explanation = "Метод относительного большинства:\n"
        explanation += "Каждый голосующий выбирает одного кандидата.\n"
        explanation += "Победитель - кандидат с наибольшим количеством голосов.\n\n"
        explanation += "Результаты:\n"
        for candidate in self.candidates:
            explanation += f"{candidate.name}: {scores[candidate.id]} голосов\n"

        return {
            "winner": winners[0] if len(winners) == 1 else None,
            "winners": winners,
            "scores": scores,
            "explanation": explanation
        }

    def condorcet_winner(self) -> Dict:
        """Победитель Кондорсе"""
        if not self.votes or len(self.candidates) < 2:
            return {"winner": None, "matrix": None, "explanation": "Недостаточно данных"}

        n = len(self.candidates)
        matrix = np.zeros((n, n))

        # Строим матрицу попарных сравнений
        for vote in self.votes:
            for i in range(n):
                for j in range(n):
                    if i != j and vote[i] < vote[j]:
                        matrix[vote[i]][vote[j]] += 1

        # Проверяем наличие победителя Кондорсе
        winner = None
        for i in range(n):
            if all(matrix[i][j] > matrix[j][i] for j in range(n) if i != j):
                winner = i
                break

        explanation = "Победитель Кондорсе:\n"
        explanation += "Кандидат, который побеждает каждого другого кандидата в попарном сравнении.\n\n"

        if winner is not None:
            explanation += f"Победитель: {self.candidates[winner].name}\n"
            for j in range(n):
                if j != winner:
                    explanation += f"Побеждает {self.candidates[j].name}: {matrix[winner][j]}:{matrix[j][winner]}\n"
        else:
            explanation += "Явного победителя нет (пароксиальный цикл)\n"

        return {
            "winner": winner,
            "matrix": matrix,
            "explanation": explanation
        }

    def copeland_rule(self) -> Dict:
        """Правило Копленда"""
        if not self.votes or len(self.candidates) < 2:
            return {"winner": None, "scores": {}, "explanation": "Недостаточно данных"}

        condorcet_result = self.condorcet_winner()
        matrix = condorcet_result["matrix"]
        n = len(self.candidates)

        # Вычисляем оценки Копленда
        scores = {}
        for i in range(n):
            score = 0
            for j in range(n):
                if i != j:
                    if matrix[i][j] > matrix[j][i]:
                        score += 1
                    elif matrix[i][j] < matrix[j][i]:
                        score -= 1
            scores[i] = score

        max_score = max(scores.values())
        winners = [cid for cid, score in scores.items() if score == max_score]

        explanation = "Правило Копленда:\n"
        explanation += "Каждой победе в попарном сравнении +1, поражению -1, ничьей 0.\n"
        explanation += "Победитель - с наибольшей суммой.\n\n"
        explanation += "Результаты:\n"
        for candidate in self.candidates:
            explanation += f"{candidate.name}: {scores[candidate.id]} баллов\n"

        return {
            "winner": winners[0] if len(winners) == 1 else None,
            "winners": winners,
            "scores": scores,
            "explanation": explanation
        }

    def simpson_rule(self) -> Dict:
        """Правило Симпсона (максимин)"""
        if not self.votes or len(self.candidates) < 2:
            return {"winner": None, "scores": {}, "explanation": "Недостаточно данных"}

        condorcet_result = self.condorcet_winner()
        matrix = condorcet_result["matrix"]
        n = len(self.candidates)

        # Вычисляем минимальные поддержки
        scores = {}
        for i in range(n):
            min_support = float('inf')
            for j in range(n):
                if i != j:
                    min_support = min(min_support, matrix[i][j])
            scores[i] = min_support

        max_score = max(scores.values())
        winners = [cid for cid, score in scores.items() if score == max_score]

        explanation = "Правило Симпсона (максимин):\n"
        explanation += "Для каждого кандидата находим минимальную поддержку против других.\n"
        explanation += "Победитель - с наибольшим минимальным значением.\n\n"
        explanation += "Результаты:\n"
        for candidate in self.candidates:
            explanation += f"{candidate.name}: минимальная поддержка {scores[candidate.id]}\n"

        return {
            "winner": winners[0] if len(winners) == 1 else None,
            "winners": winners,
            "scores": scores,
            "explanation": explanation
        }

    def borda_count(self) -> Dict:
        """Метод Борда"""
        if not self.votes:
            return {"winner": None, "scores": {}, "explanation": "Нет голосов"}

        n = len(self.candidates)
        scores = {candidate.id: 0 for candidate in self.candidates}

        # Подсчет очков Борда
        for vote in self.votes:
            for rank, candidate_id in enumerate(vote):
                scores[candidate_id] += (n - rank - 1)  # 1-е место: n-1 очков, последнее: 0

        max_score = max(scores.values())
        winners = [cid for cid, score in scores.items() if score == max_score]

        explanation = "Метод Борда:\n"
        explanation += "Каждый голосующий ранжирует кандидатов.\n"
        explanation += f"За 1-е место: {n - 1} очков, за 2-е: {n - 2} и т.д.\n\n"
        explanation += "Результаты:\n"
        for candidate in self.candidates:
            explanation += f"{candidate.name}: {scores[candidate.id]} очков\n"

        return {
            "winner": winners[0] if len(winners) == 1 else None,
            "winners": winners,
            "scores": scores,
            "explanation": explanation
        }


class ElectionApp:
    """Графический интерфейс для системы выборов"""

    def __init__(self, root):
        self.root = root
        self.root.title("Система выборов старосты группы")
        self.root.geometry("1200x700")

        self.vote_system = VoteSystem()
        self.current_voter = 0
        self.setup_ui()
        self.load_sample_data()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Создаем панель с вкладками
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладка 1: Добавление кандидатов
        self.candidates_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.candidates_tab, text="Кандидаты")
        self.setup_candidates_tab()

        # Вкладка 2: Голосование
        self.voting_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.voting_tab, text="Голосование")
        self.setup_voting_tab()

        # Вкладка 3: Результаты
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="Результаты")
        self.setup_results_tab()

        # Вкладка 4: Справка
        self.help_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.help_tab, text="Справка")
        self.setup_help_tab()

    def setup_candidates_tab(self):
        """Настройка вкладки кандидатов"""
        # Левая панель - добавление кандидатов
        left_frame = ttk.LabelFrame(self.candidates_tab, text="Добавить кандидата", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(left_frame, text="ФИО кандидата:").pack(anchor=tk.W, pady=(0, 5))
        self.name_entry = ttk.Entry(left_frame, width=30)
        self.name_entry.pack(pady=(0, 10))

        ttk.Label(left_frame, text="Описание (достоинства):").pack(anchor=tk.W, pady=(0, 5))
        self.desc_text = tk.Text(left_frame, height=5, width=30)
        self.desc_text.pack(pady=(0, 10))

        # Кнопки для быстрого добавления
        # ttk.Label(left_frame, text="Быстрое добавление:").pack(anchor=tk.W, pady=(0, 5))

        # quick_names = ["Иванов И.И.", "Петрова А.С.", "Сидоров В.В.", "Козлова Е.П."]
        # for name in quick_names:
        #    btn = ttk.Button(left_frame, text=name,
        #                     command=lambda n=name: self.quick_add_candidate(n))
        #    btn.pack(pady=2)

        add_btn = ttk.Button(left_frame, text="Добавить кандидата",
                             command=self.add_candidate)
        add_btn.pack(pady=10)

        # Правая панель - список кандидатов
        right_frame = ttk.LabelFrame(self.candidates_tab, text="Список кандидатов", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Таблица кандидатов
        columns = ("ID", "ФИО", "Описание")
        self.candidates_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.candidates_tree.heading(col, text=col)
            self.candidates_tree.column(col, width=100)

        self.candidates_tree.pack(fill=tk.BOTH, expand=True)

        # Кнопка удаления
        del_btn = ttk.Button(right_frame, text="Удалить выбранного",
                             command=self.delete_candidate)
        del_btn.pack(pady=10)

    def setup_voting_tab(self):
        """Настройка вкладки голосования"""
        main_frame = ttk.Frame(self.voting_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Информация о текущем голосующем
        info_frame = ttk.LabelFrame(main_frame, text="Голосующий", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self.voter_label = ttk.Label(info_frame, text="Голосующий #1", font=("Arial", 12, "bold"))
        self.voter_label.pack()

        ttk.Label(info_frame, text="Расставьте кандидатов в порядке предпочтения (1 - самый предпочтительный):").pack()

        # Область для голосования
        voting_frame = ttk.LabelFrame(main_frame, text="Бюллетень", padding=15)
        voting_frame.pack(fill=tk.BOTH, expand=True)

        self.rank_vars = []
        self.rank_combos = []

        # Создаем выпадающие списки для ранжирования
        for i in range(5):  # Максимум 5 кандидатов
            frame = ttk.Frame(voting_frame)
            frame.pack(fill=tk.X, pady=5)

            ttk.Label(frame, text=f"{i + 1}-е место:", width=10).pack(side=tk.LEFT)

            var = tk.StringVar()
            combo = ttk.Combobox(frame, textvariable=var, width=30, state="readonly")
            combo.pack(side=tk.LEFT, padx=5)

            self.rank_vars.append(var)
            self.rank_combos.append(combo)

        # Кнопки управления голосованием
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="Проголосовать",
                   command=self.cast_vote).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Следующий голосующий",
                   command=self.next_voter).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Сбросить голоса",
                   command=self.reset_votes).pack(side=tk.RIGHT, padx=5)

        # Статистика
        stats_frame = ttk.LabelFrame(main_frame, text="Статистика", padding=10)
        stats_frame.pack(fill=tk.X, pady=(10, 0))

        self.stats_label = ttk.Label(stats_frame, text="Всего голосов: 0")
        self.stats_label.pack()

    def setup_results_tab(self):
        """Настройка вкладки результатов"""
        # Левая панель - выбор метода
        left_frame = ttk.Frame(self.results_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        methods_frame = ttk.LabelFrame(left_frame, text="Методы голосования", padding=10)
        methods_frame.pack(fill=tk.X, pady=(0, 10))

        self.method_var = tk.StringVar(value="plurality")

        methods = [
            ("Относительное большинство", "plurality"),
            ("Победитель Кондорсе", "condorcet"),
            ("Правило Копленда", "copeland"),
            ("Правило Симпсона", "simpson"),
            ("Метод Борда", "borda")
        ]

        for text, value in methods:
            rb = ttk.Radiobutton(methods_frame, text=text, variable=self.method_var,
                                 value=value, command=self.show_results)
            rb.pack(anchor=tk.W, pady=2)

        calc_btn = ttk.Button(methods_frame, text="Рассчитать все методы",
                              command=self.show_all_results)
        calc_btn.pack(pady=10)

        # График результатов
        self.figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, left_frame)
        self.canvas.get_tk_widget().pack(pady=10)
        self.ax.tick_params(axis='x', labelsize=5)  # Размер 8 пунктов

        # Правая панель - объяснение результатов
        right_frame = ttk.Frame(self.results_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(right_frame, text="Объяснение результатов:",
                  font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=(0, 10))

        # Текстовое поле с прокруткой
        text_frame = ttk.Frame(right_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.results_text = tk.Text(text_frame, wrap=tk.WORD, width=60, height=20)
        scrollbar = ttk.Scrollbar(text_frame, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)

        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Область для победителя
        winner_frame = ttk.LabelFrame(right_frame, text="Победитель", padding=10)
        winner_frame.pack(fill=tk.X, pady=(10, 0))

        self.winner_label = ttk.Label(winner_frame, text="",
                                      font=("Arial", 14, "bold"), foreground="green")
        self.winner_label.pack()

    def setup_help_tab(self):
        """Настройка вкладки справки"""
        help_text = """
        СИСТЕМА ВЫБОРОВ СТАРОСТЫ ГРУППЫ

        Инструкция:

        1. Вкладка "Кандидаты":
           - Добавьте кандидатов на пост старосты
           - Используйте кнопки для быстрого добавления
           - Можно добавить описание достоинств кандидата

        2. Вкладка "Голосование":
           - Каждый голосующий ранжирует кандидатов по предпочтению
           - 1-е место - самый предпочтительный кандидат
           - Нажмите "Проголосовать" для сохранения голоса
           - "Следующий голосующий" - переходит к следующему

        3. Вкладка "Результаты":
           - Выберите метод подсчета голосов
           - Нажмите "Рассчитать все методы" для сравнения
           - Результаты отображаются с объяснением

        Методы голосования:

        • Относительное большинство: простой подсчет первых предпочтений
        • Победитель Кондорсе: кандидат, побеждающий всех в попарных сравнениях
        • Правило Копленда: +1 за победу, -1 за поражение в попарных сравнениях
        • Правило Симпсона: выбирается кандидат с наибольшей минимальной поддержкой
        • Метод Борда: ранжирование с начислением очков за места

        Рекомендации:
        - Добавьте минимум 3 кандидата
        - Для демонстрации достаточно 5-10 голосующих
        - Сравните результаты разных методов
        """

        text_widget = tk.Text(self.help_tab, wrap=tk.WORD, width=80, height=30)
        text_widget.insert(1.0, help_text)
        text_widget.configure(state='disabled')

        scrollbar = ttk.Scrollbar(self.help_tab, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_sample_data(self):
        """Загрузка тестовых данных"""
        sample_candidates = [
            ("Иванов Иван Иванович", "Отличник, активный, ответственный"),
            ("Петрова Анна Сергеевна", "Коммуникабельная, организатор, хорошая успеваемость"),
            ("Сидоров Владимир Владимирович", "Спортсмен, лидер, справедливый"),
            ("Козлова Елена Петровна", "Добросовестная, отзывчивая, аккуратная")
        ]

        for name, desc in sample_candidates:
            self.vote_system.add_candidate(name, desc)

        # Обновляем интерфейс
        self.update_candidates_list()
        self.update_voting_combos()

        # Добавляем несколько тестовых голосов
        test_votes = [
            [0, 1, 2, 3],  # Иванов -> Петрова -> Сидоров -> Козлова
            [1, 0, 3, 2],
            [0, 2, 1, 3],
            [0, 2, 1, 3],
            [1, 3, 0, 2],
            [0, 1, 2, 3],  # Иванов -> Петрова -> Сидоров -> Козлова
            [1, 0, 3, 2],
            [2, 3, 1, 0],
            [0, 2, 3, 1],
            [1, 3, 0, 2]

        ]

        for vote in test_votes:
            self.vote_system.add_vote(vote)

        self.update_stats()

    def quick_add_candidate(self, name):
        """Быстрое добавление кандидата"""
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, name)
        self.desc_text.delete(1.0, tk.END)
        self.add_candidate()

    def add_candidate(self):
        """Добавление нового кандидата"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Введите ФИО кандидата")
            return

        description = self.desc_text.get(1.0, tk.END).strip()

        self.vote_system.add_candidate(name, description)

        # Очистка полей
        self.name_entry.delete(0, tk.END)
        self.desc_text.delete(1.0, tk.END)

        # Обновление интерфейса
        self.update_candidates_list()
        self.update_voting_combos()
        messagebox.showinfo("Успех", f"Кандидат {name} добавлен")

    def delete_candidate(self):
        """Удаление выбранного кандидата"""
        selection = self.candidates_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите кандидата для удаления")
            return

        item = self.candidates_tree.item(selection[0])
        candidate_id = int(item['values'][0])

        # Удаляем кандидата из системы
        if 0 <= candidate_id < len(self.vote_system.candidates):
            del self.vote_system.candidates[candidate_id]

            # Обновляем ID оставшихся кандидатов
            for i, candidate in enumerate(self.vote_system.candidates):
                candidate.id = i

            # Очищаем голоса
            self.vote_system.votes = []
            self.current_voter = 0
            self.update_stats()

            self.update_candidates_list()
            self.update_voting_combos()

            messagebox.showinfo("Успех", "Кандидат удален")

    def update_candidates_list(self):
        """Обновление списка кандидатов"""
        # Очистка дерева
        for item in self.candidates_tree.get_children():
            self.candidates_tree.delete(item)

        # Заполнение новыми данными
        for candidate in self.vote_system.candidates:
            self.candidates_tree.insert("", tk.END, values=(
                candidate.id,
                candidate.name,
                candidate.description[:50] + "..." if len(candidate.description) > 50 else candidate.description
            ))

    def update_voting_combos(self):
        """Обновление выпадающих списков для голосования"""
        candidate_names = [candidate.name for candidate in self.vote_system.candidates]

        for combo in self.rank_combos:
            combo['values'] = candidate_names
            combo.set('')  # Очищаем текущее значение

        # Скрываем лишние комбобоксы если кандидатов меньше
        for i in range(len(self.rank_combos)):
            if i < len(candidate_names):
                self.rank_combos[i].config(state="readonly")
            else:
                self.rank_combos[i].config(state="disabled")
                self.rank_vars[i].set('')

    def cast_vote(self):
        """Обработка голосования"""
        # Проверяем, что все места заполнены
        candidate_names = [candidate.name for candidate in self.vote_system.candidates]
        selected_names = []

        for i in range(len(candidate_names)):
            name = self.rank_vars[i].get()
            if not name:
                messagebox.showwarning("Внимание", f"Заполните {i + 1}-е место")
                return
            if name in selected_names:
                messagebox.showwarning("Внимание", "Кандидат выбран более одного раза")
                return
            selected_names.append(name)

        # Преобразуем имена в ID
        name_to_id = {candidate.name: candidate.id for candidate in self.vote_system.candidates}
        try:
            preferences = [name_to_id[name] for name in selected_names]
        except KeyError:
            messagebox.showerror("Ошибка", "Ошибка обработки голоса")
            return

        # Добавляем голос
        self.vote_system.add_vote(preferences)
        self.current_voter += 1
        self.update_stats()

        # Очищаем форму
        for var in self.rank_vars:
            var.set('')

        messagebox.showinfo("Успех", f"Голос #{self.current_voter} сохранен!")

    def next_voter(self):
        """Переход к следующему голосующему"""
        self.current_voter += 1
        self.voter_label.config(text=f"Голосующий #{self.current_voter + 1}")

        # Очищаем форму
        for var in self.rank_vars:
            var.set('')

    def reset_votes(self):
        """Сброс всех голосов"""
        if messagebox.askyesno("Подтверждение", "Удалить все голоса?"):
            self.vote_system.votes = []
            self.current_voter = 0
            self.update_stats()
            messagebox.showinfo("Успех", "Все голоса сброшены")

    def update_stats(self):
        """Обновление статистики"""
        total_votes = len(self.vote_system.votes)
        self.stats_label.config(text=f"Всего голосов: {total_votes}")
        self.voter_label.config(text=f"Голосующий #{total_votes + 1}")

    def show_results(self):
        """Отображение результатов выбранного метода"""
        method = self.method_var.get()

        if method == "plurality":
            result = self.vote_system.plurality()
        elif method == "condorcet":
            result = self.vote_system.condorcet_winner()
        elif method == "copeland":
            result = self.vote_system.copeland_rule()
        elif method == "simpson":
            result = self.vote_system.simpson_rule()
        elif method == "borda":
            result = self.vote_system.borda_count()
        else:
            return

        # Отображаем объяснение
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, result.get("explanation", "Нет данных"))

        # Отображаем победителя
        winner_id = result.get("winner")
        if winner_id is not None:
            winner_name = self.vote_system.candidates[winner_id].name
            self.winner_label.config(text=f"Победитель: {winner_name}")
        else:
            winners = result.get("winners", [])
            if winners:
                winner_names = [self.vote_system.candidates[w].name for w in winners]
                self.winner_label.config(text=f"Победители: {', '.join(winner_names)}")
            else:
                self.winner_label.config(text="Победитель не определен")

        # Строим график
        self.create_bar_chart(result)

    def show_all_results(self):
        """Отображение результатов всех методов"""
        methods = ["plurality", "condorcet", "copeland", "simpson", "borda"]
        method_names = ["Относительное большинство", "Кондорсе", "Копленд", "Симпсон", "Борда"]
        winners = []

        all_results = ""

        for method_name, method in zip(method_names, methods):
            if method == "plurality":
                result = self.vote_system.plurality()
            elif method == "condorcet":
                result = self.vote_system.condorcet_winner()
            elif method == "copeland":
                result = self.vote_system.copeland_rule()
            elif method == "simpson":
                result = self.vote_system.simpson_rule()
            elif method == "borda":
                result = self.vote_system.borda_count()

            winner_id = result.get("winner")
            if winner_id is not None:
                winner_name = self.vote_system.candidates[winner_id].name
                winners.append((method_name, winner_name))
            else:
                winners.append((method_name, "не определен"))

            all_results += f"=== {method_name} ===\n"
            all_results += result.get("explanation", "") + "\n\n"

        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, all_results)

        # Сводная таблица победителей
        summary = "\n" + "=" * 50 + "\n"
        summary += "Сводная таблица победителей:\n" + "=" * 50 + "\n"
        for method, winner in winners:
            summary += f"{method:25} : {winner}\n"

        self.results_text.insert(tk.END, summary)

        # Отображаем последний результат
        self.winner_label.config(text=f"Сравните результаты разных методов")

    def create_bar_chart(self, result):
        """Создание столбчатой диаграммы"""
        self.ax.clear()

        scores = result.get("scores", {})
        if not scores:
            self.ax.text(0.5, 0.5, 'Нет данных',
                         horizontalalignment='center',
                         verticalalignment='center',
                         transform=self.ax.transAxes)
        else:
            candidates = [self.vote_system.candidates[cid].name for cid in scores.keys()]
            values = list(scores.values())

            colors = ['lightblue' for _ in candidates]
            winner_id = result.get("winner")
            if winner_id is not None:
                colors[list(scores.keys()).index(winner_id)] = 'green'

            bars = self.ax.bar(candidates, values, color=colors)
            self.ax.set_ylabel('Баллы' if 'Борда' in result.get("explanation", "") else 'Голоса')
            self.ax.set_title('Результаты голосования')

            # Добавляем значения над столбцами
            for bar, value in zip(bars, values):
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width() / 2., height,
                             f'{value}', ha='center', va='bottom')

        self.figure.tight_layout()
        self.canvas.draw()


def main():
    """Основная функция запуска приложения"""
    root = tk.Tk()
    app = ElectionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()