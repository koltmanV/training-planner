import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

DATE_FMT = "%Y-%m-%d"
TRAINING_TYPES = ["Силовая", "Кардио", "Йога", "Плавание", "Бег", "Другое"]
DEFAULT_FILE = "trainings.json"

class TrainingPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("1000x680")
        self.root.minsize(920, 600)
        self.trainings = []
        self.filtered_trainings = []
        self.date_var = tk.StringVar(value=datetime.now().strftime(DATE_FMT))
        self.type_var = tk.StringVar(value=TRAINING_TYPES[0])
        self.duration_var = tk.StringVar()
        self.filter_type_var = tk.StringVar(value="Все")
        self.filter_date_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Готово к работе")
        self._build_ui()
        self.refresh_table()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(2, weight=1)

        form = ttk.LabelFrame(main, text="Добавление тренировки", padding=10)
        form.grid(row=0, column=0, sticky="ew")
        for i in range(6):
            form.columnconfigure(i, weight=1)

        ttk.Label(form, text="Дата (ГГГГ-ММ-ДД)").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.date_var).grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ttk.Label(form, text="Тип тренировки").grid(row=0, column=1, sticky="w")
        ttk.Combobox(form, textvariable=self.type_var, values=TRAINING_TYPES, state="readonly").grid(row=1, column=1, sticky="ew", padx=(0, 8))
        ttk.Label(form, text="Длительность (мин)").grid(row=0, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.duration_var).grid(row=1, column=2, sticky="ew", padx=(0, 8))
        ttk.Button(form, text="Добавить тренировку", command=self.add_training).grid(row=1, column=3, sticky="ew", padx=(0, 8))
        ttk.Button(form, text="Сохранить JSON", command=self.save_json).grid(row=1, column=4, sticky="ew", padx=(0, 8))
        ttk.Button(form, text="Загрузить JSON", command=self.load_json).grid(row=1, column=5, sticky="ew")

        filt = ttk.LabelFrame(main, text="Фильтрация", padding=10)
        filt.grid(row=1, column=0, sticky="ew", pady=12)
        for i in range(6):
            filt.columnconfigure(i, weight=1)

        ttk.Label(filt, text="Тип тренировки").grid(row=0, column=0, sticky="w")
        ttk.Combobox(filt, textvariable=self.filter_type_var, values=["Все"] + TRAINING_TYPES, state="readonly").grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ttk.Label(filt, text="Дата").grid(row=0, column=1, sticky="w")
        ttk.Entry(filt, textvariable=self.filter_date_var).grid(row=1, column=1, sticky="ew", padx=(0, 8))
        ttk.Button(filt, text="Применить фильтр", command=self.apply_filter).grid(row=1, column=2, sticky="ew", padx=(0, 8))
        ttk.Button(filt, text="Сбросить фильтр", command=self.reset_filter).grid(row=1, column=3, sticky="ew")

        table_frame = ttk.LabelFrame(main, text="План тренировок", padding=10)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        columns = ("id", "date", "type", "duration")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=16)
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип")
        self.tree.heading("duration", text="Длительность")
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("date", width=150, anchor="center")
        self.tree.column("type", width=220, anchor="center")
        self.tree.column("duration", width=130, anchor="center")
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        bottom = ttk.Frame(main)
        bottom.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        bottom.columnconfigure(0, weight=1)
        ttk.Label(bottom, textvariable=self.status_var, relief="sunken", anchor="w", padding=6).grid(row=0, column=0, sticky="ew")
        ttk.Button(bottom, text="Удалить выбранное", command=self.delete_selected).grid(row=0, column=1, padx=(8, 0))

    def _validate_date(self, value):
        try:
            return datetime.strptime(value.strip(), DATE_FMT).date()
        except ValueError:
            raise ValueError("Дата должна быть в формате ГГГГ-ММ-ДД.")

    def _validate_duration(self, value):
        try:
            duration = float(value.replace(",", "."))
        except ValueError:
            raise ValueError("Длительность должна быть числом.")
        if duration <= 0:
            raise ValueError("Длительность должна быть положительным числом.")
        return round(duration, 1)

    def add_training(self):
        try:
            date_obj = self._validate_date(self.date_var.get())
            duration = self._validate_duration(self.duration_var.get())
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return

        item = {
            "id": len(self.trainings) + 1,
            "date": date_obj.strftime(DATE_FMT),
            "type": self.type_var.get(),
            "duration": duration,
        }
        self.trainings.append(item)
        self.refresh_table(self.trainings)
        self.duration_var.set("")
        self.status_var.set(f"Добавлена тренировка: {item['date']} | {item['type']} | {item['duration']} мин")

    def refresh_table(self, data=None):
        data = self.trainings if data is None else data
        self.filtered_trainings = list(data)
        self.tree.delete(*self.tree.get_children())
        for item in data:
            self.tree.insert("", "end", values=(item["id"], item["date"], item["type"], item["duration"]))

    def apply_filter(self):
        ttype = self.filter_type_var.get()
        date_text = self.filter_date_var.get().strip()
        try:
            date_filter = None
            if date_text:
                date_filter = self._validate_date(date_text)
        except ValueError as e:
            messagebox.showerror("Ошибка фильтра", str(e))
            return

        filtered = []
        for item in self.trainings:
            item_date = datetime.strptime(item["date"], DATE_FMT).date()
            if ttype != "Все" and item["type"] != ttype:
                continue
            if date_filter and item_date != date_filter:
                continue
            filtered.append(item)
        self.refresh_table(filtered)
        self.status_var.set(f"Фильтр применён. Найдено: {len(filtered)}")

    def reset_filter(self):
        self.filter_type_var.set("Все")
        self.filter_date_var.set("")
        self.refresh_table(self.trainings)
        self.status_var.set("Фильтр сброшен")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Удаление", "Выберите запись в таблице.")
            return
        item_id = int(self.tree.item(selected[0], "values")[0])
        self.trainings = [x for x in self.trainings if x["id"] != item_id]
        for idx, item in enumerate(self.trainings, start=1):
            item["id"] = idx
        self.refresh_table(self.trainings)
        self.status_var.set(f"Удалена запись ID {item_id}")

    def save_json(self):
        path = filedialog.asksaveasfilename(title="Сохранить JSON", defaultextension=".json", initialfile=DEFAULT_FILE, filetypes=[("JSON files", "*.json")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.trainings, f, ensure_ascii=False, indent=4)
        self.status_var.set(f"Сохранено: {os.path.basename(path)}")
        messagebox.showinfo("Сохранение", "Данные успешно сохранены.")

    def load_json(self):
        path = filedialog.askopenfilename(title="Загрузить JSON", filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            loaded = []
            for i, item in enumerate(data, start=1):
                date_obj = self._validate_date(str(item.get("date", "")))
                duration = self._validate_duration(str(item.get("duration", "")))
                ttype = str(item.get("type", "Другое")).strip() or "Другое"
                if ttype not in TRAINING_TYPES:
                    ttype = "Другое"
                loaded.append({"id": i, "date": date_obj.strftime(DATE_FMT), "type": ttype, "duration": duration})
            self.trainings = loaded
            self.refresh_table(self.trainings)
            self.status_var.set(f"Загружено записей: {len(self.trainings)}")
            messagebox.showinfo("Загрузка", "Данные успешно загружены.")
        except (json.JSONDecodeError, OSError, ValueError) as e:
            messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить файл: {e}")


def main():
    root = tk.Tk()
    TrainingPlannerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
