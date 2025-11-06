import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from PIL import Image, ImageTk
from io import BytesIO
import sqlite3
from datetime import datetime


class GiftCardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор Telegram Gifts")
        self.root.geometry("800x700")


        self.init_db()

        input_frame = ttk.LabelFrame(root, text="Параметры карты", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(input_frame, text="Основной цвет:").grid(row=0, column=0, sticky=tk.W)
        self.primary_color = ttk.Entry(input_frame, width=10)
        self.primary_color.grid(row=0, column=1, sticky=tk.W)
        self.primary_color.insert(0, "#FF5733")

        ttk.Label(input_frame, text="Вторичный цвет:").grid(row=1, column=0, sticky=tk.W)
        self.secondary_color = ttk.Entry(input_frame, width=10)
        self.secondary_color.grid(row=1, column=1, sticky=tk.W)
        self.secondary_color.insert(0, "#33FF57")

        ttk.Label(input_frame, text="Цена в USD:").grid(row=2, column=0, sticky=tk.W)
        self.price_usd = ttk.Entry(input_frame, width=10)
        self.price_usd.grid(row=2, column=1, sticky=tk.W)
        self.price_usd.insert(0, "100")

        ttk.Label(input_frame, text="Цена в звездах:").grid(row=3, column=0, sticky=tk.W)
        self.price_star = ttk.Entry(input_frame, width=10)
        self.price_star.grid(row=3, column=1, sticky=tk.W)
        self.price_star.insert(0, "500")

        ttk.Label(input_frame, text="Цена в TON:").grid(row=4, column=0, sticky=tk.W)
        self.price_ton = ttk.Entry(input_frame, width=10)
        self.price_ton.grid(row=4, column=1, sticky=tk.W)
        self.price_ton.insert(0, "10")

        ttk.Label(input_frame, text="Название подарка:").grid(row=5, column=0, sticky=tk.W)
        self.gift_name = ttk.Entry(input_frame, width=30)
        self.gift_name.grid(row=5, column=1, sticky=tk.W)
        self.gift_name.insert(0, "Premium Box")

        ttk.Label(input_frame, text="URL изображения:").grid(row=6, column=0, sticky=tk.W)
        self.gift_image = ttk.Entry(input_frame, width=40)
        self.gift_image.grid(row=6, column=1, sticky=tk.W)
        self.gift_image.insert(0, "https://i.postimg.cc/jR6TNBW5/Plush-Pepe-Gift.png?dl=1")

        ttk.Label(input_frame, text="Количество:").grid(row=7, column=0, sticky=tk.W)
        self.gift_quantity = ttk.Entry(input_frame, width=10)
        self.gift_quantity.grid(row=7, column=1, sticky=tk.W)
        self.gift_quantity.insert(0, "1")

        ttk.Label(input_frame, text="Время:").grid(row=8, column=0, sticky=tk.W)
        self.time_display = ttk.Entry(input_frame, width=10)
        self.time_display.grid(row=8, column=1, sticky=tk.W)
        self.time_display.insert(0, "24h")


        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)

        generate_btn = ttk.Button(button_frame, text="Сгенерировать карту", command=self.generate_card)
        generate_btn.pack(side=tk.LEFT, padx=5)

        history_btn = ttk.Button(button_frame, text="История запросов", command=self.show_history)
        history_btn.pack(side=tk.LEFT, padx=5)

        self.image_frame = ttk.LabelFrame(root, text="Результат", padding=10)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(expand=True)

    def init_db(self):

        self.conn = sqlite3.connect('gift_card_history.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS gift_card_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                primary_color TEXT,
                secondary_color TEXT,
                price_usd INTEGER,
                price_star INTEGER,
                price_ton INTEGER,
                gift_name TEXT,
                gift_image TEXT,
                gift_quantity INTEGER,
                time_display TEXT,
                response_status INTEGER
            )
        ''')
        self.conn.commit()

    def save_to_db(self, data, response_status):

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute('''
            INSERT INTO gift_card_requests 
            (timestamp, primary_color, secondary_color, price_usd, price_star, price_ton, 
             gift_name, gift_image, gift_quantity, time_display, response_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            data["background_gradient"]["primary_color"],
            data["background_gradient"]["secondary_color"],
            data["price"]["usd"],
            data["price"]["star"],
            data["price"]["ton"],
            data["gift"]["name"],
            data["gift"]["image"],
            data["gift"]["quantity"],
            data["time_display"],
            response_status
        ))
        self.conn.commit()

    def generate_card(self):
        try:
            data = {
                "background_gradient": {
                    "primary_color": self.primary_color.get(),
                    "secondary_color": self.secondary_color.get()
                },
                "price": {
                    "usd": int(self.price_usd.get()),
                    "star": int(self.price_star.get()),
                    "ton": int(self.price_ton.get())
                },
                "gift": {
                    "name": self.gift_name.get(),
                    "image": self.gift_image.get(),
                    "quantity": int(self.gift_quantity.get())
                },
                "time_display": self.time_display.get()
            }

            url = "http://localhost:8003/generate_gift_card"

            response = requests.post(url, json=data)


            self.save_to_db(data, response.status_code)

            if response.status_code == 200:
                img_data = BytesIO(response.content)
                img = Image.open(img_data)

                img.thumbnail((500, 700))

                photo = ImageTk.PhotoImage(img)

                self.image_label.config(image=photo)
                self.image_label.image = photo

                messagebox.showinfo("Успех", "Карта успешно сгенерирована и сохранена в историю!")
            else:
                messagebox.showerror("Ошибка", f"Ошибка сервера: {response.status_code}\n{response.text}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def show_history(self):

        history_window = tk.Toplevel(self.root)
        history_window.title("История запросов")
        history_window.geometry("900x500")


        tree = ttk.Treeview(history_window, columns=("ID", "Время", "Основной цвет", "Вторичный цвет",
                                                     "USD", "Звезды", "TON", "Название", "Статус"), show="headings")


        tree.heading("ID", text="ID")
        tree.heading("Время", text="Время запроса")
        tree.heading("Основной цвет", text="Основной цвет")
        tree.heading("Вторичный цвет", text="Вторичный цвет")
        tree.heading("USD", text="USD")
        tree.heading("Звезды", text="Звезды")
        tree.heading("TON", text="TON")
        tree.heading("Название", text="Название подарка")
        tree.heading("Статус", text="Статус")

        tree.column("ID", width=50)
        tree.column("Время", width=150)
        tree.column("Основной цвет", width=100)
        tree.column("Вторичный цвет", width=100)
        tree.column("USD", width=80)
        tree.column("Звезды", width=80)
        tree.column("TON", width=80)
        tree.column("Название", width=150)
        tree.column("Статус", width=100)


        scrollbar = ttk.Scrollbar(history_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)


        self.cursor.execute('''
            SELECT id, timestamp, primary_color, secondary_color, price_usd, 
                   price_star, price_ton, gift_name, response_status
            FROM gift_card_requests 
            ORDER BY id DESC
        ''')
        records = self.cursor.fetchall()


        for record in records:
            status_text = "Успех" if record[8] == 200 else f"Ошибка {record[8]}"
            tree.insert("", 0, values=(
                record[0], record[1], record[2], record[3],
                record[4], record[5], record[6], record[7], status_text
            ))


        def show_details():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Предупреждение", "Выберите запрос для просмотра деталей")
                return

            item = tree.item(selected_item[0])
            record_id = item['values'][0]


            self.cursor.execute('SELECT * FROM gift_card_requests WHERE id = ?', (record_id,))
            full_record = self.cursor.fetchone()


            details_window = tk.Toplevel(history_window)
            details_window.title(f"Детали запроса #{record_id}")
            details_window.geometry("400x300")

            details_text = f"""Детали запроса #{record_id}:

Время: {full_record[1]}
Основной цвет: {full_record[2]}
Вторичный цвет: {full_record[3]}
Цена в USD: {full_record[4]}
Цена в звездах: {full_record[5]}
Цена в TON: {full_record[6]}
Название подарка: {full_record[7]}
URL изображения: {full_record[8]}
Количество: {full_record[9]}
Время отображения: {full_record[10]}
Статус ответа: {full_record[11]}
"""

            text_widget = tk.Text(details_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.insert(1.0, details_text)
            text_widget.config(state=tk.DISABLED)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


        def clear_history():
            if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
                self.cursor.execute('DELETE FROM gift_card_requests')
                self.conn.commit()

                for item in tree.get_children():
                    tree.delete(item)
                messagebox.showinfo("Успех", "История очищена")


        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        button_frame = ttk.Frame(history_window)
        button_frame.pack(pady=10)

        details_btn = ttk.Button(button_frame, text="Просмотреть детали", command=show_details)
        details_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(button_frame, text="Очистить историю", command=clear_history)
        clear_btn.pack(side=tk.LEFT, padx=5)

        close_btn = ttk.Button(button_frame, text="Закрыть", command=history_window.destroy)
        close_btn.pack(side=tk.LEFT, padx=5)

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()


root = tk.Tk()
app = GiftCardApp(root)
root.mainloop()