import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

# --- КОНФИГУРАЦИЯ ---
API_KEY = "ВАШ_API_KEY" # <--- ВСТАВЬТЕ СЮДА
BASE_URL = f"https://exchangerate-api.com{API_KEY}/latest/"
HISTORY_FILE = "history.json"

# --- ЛОГИКА ---
def get_exchange_rate(from_currency, to_currency):
    try:
        response = requests.get(f"{BASE_URL}{from_currency}")
        data = response.json()
        if data["result"] == "success":
            return data["conversion_rates"][to_currency]
        else:
            return None
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка сети: {e}")
        return None

def save_history(record):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except:
                history = []
    history.append(record)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

# --- GUI ---
def convert():
    amount = amount_entry.get()
    from_curr = from_combo.get()
    to_curr = to_combo.get()

    # Валидация
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Ошибка", "Введите положительное число")
        return

    rate = get_exchange_rate(from_curr, to_curr)
    if rate:
        result = amount * rate
        result_label.config(text=f"{result:.2f} {to_curr}")
        
        # Сохранение
        record = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
            "result": round(result, 2)
        }
        save_history(record)
        update_table()

def update_table():
    for i in tree.get_children():
        tree.delete(i)
    history = load_history()
    for row in reversed(history[-10:]): # Показываем последние 10
        tree.insert("", "end", values=(row["time"], f"{row['amount']} {row['from']}", f"{row['result']} {row['to']}"))

# Интерфейс
app = tk.Tk()
app.title("Currency Converter")
app.geometry("500x550")

# Ввод
tk.Label(app, text="Сумма:").pack(pady=5)
amount_entry = tk.Entry(app)
amount_entry.pack()

currencies = ["USD", "EUR", "RUB", "GBP", "JPY"]
tk.Label(app, text="Из:").pack(pady=5)
from_combo = ttk.Combobox(app, values=currencies)
from_combo.current(0)
from_combo.pack()

tk.Label(app, text="В:").pack(pady=5)
to_combo = ttk.Combobox(app, values=currencies)
to_combo.current(1)
to_combo.pack()

btn = tk.Button(app, text="Конвертировать", command=convert)
btn.pack(pady=15)

result_label = tk.Label(app, text="", font=("Arial", 16, "bold"))
result_label.pack(pady=10)

# Таблица истории
tree = ttk.Treeview(app, columns=("Time", "From", "To"), show="headings", height=8)
tree.heading("Time", text="Время")
tree.heading("From", text="Сумма")
tree.heading("To", text="Результат")
tree.column("Time", width=150)
tree.pack(pady=10, fill=tk.BOTH, expand=True)

update_table()
app.mainloop()
