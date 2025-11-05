import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import requests
from io import BytesIO
from PIL import Image, ImageTk
import sqlite3
import sys


class GiftCardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор Telegram Gifts")
        self.root.geometry("800x700")

        # Блокируем закрытие через крестик, чтобы видеть ошибки
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Параметры подключения к MySQL
        self.db_config = {
            'host': 'mysql2.joinserver.xyz',
            'port': 3306,
            'database': 's410037_NKEiVT2',
            'user': 'u410037_re3IqhHAoH',
            'password': 'hnOw+LKzGcHrMtLt!QU5=A=w'
        }

        try:
            self.create_widgets()
            self.init_db()
            print("✅ Приложение успешно инициализировано")
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            messagebox.showerror("Ошибка", f"Не удалось запустить приложение: {str(e)}")

    def on_close(self):
        """Обработчик закрытия окна"""
        print("Закрытие приложения...")
        self.root.destroy()
        sys.exit()

    def create_widgets(self):
        """Создание элементов интерфейса"""
        print("Создание интерфейса...")

        # Основной фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм параметров
        input_frame = ttk.LabelFrame(main_frame, text="Параметры карты", padding=10)
        input_frame.pack(fill=tk.X, pady=5)

        # Создаем сетку для полей ввода
        row = 0

        # Основной цвет
        ttk.Label(input_frame, text="Основной цвет:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.primary_color = ttk.Entry(input_frame, width=10)
        self.primary_color.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        self.primary_color.insert(0, "#FF5733")
        row += 1

        # Вторичный цвет
        ttk.Label(input_frame, text="Вторичный цвет:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.secondary_color = ttk.Entry(input_frame, width=10)
        self.secondary_color.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        self.secondary_color.insert(0, "#33FF57")
        row += 1

        # Цена в USD
        ttk.Label(input_frame, text="Цена в USD:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.price_usd = ttk.Entry(input_frame, width=10)
        self.price_usd.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        self.price_usd.insert(0, "100")
        row += 1

        # Цена в звездах
        ttk.Label(input_frame, text="Цена в звездах:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.price_star = ttk.Entry(input_frame, width=10)
        self.price_star.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        self.price_star.insert(0, "500")
        row += 1

        # Цена в TON
        ttk.Label(input_frame, text="Цена в TON:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.price_ton = ttk.Entry(input_frame, width=10)
        self.price_ton.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        self.price_ton.insert(0, "10")
        row += 1

        # Название подарка
        ttk.Label(input_frame, text="Название подарка:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.gift_name = ttk.Entry(input_frame, width=30)
        self.gift_name.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        self.gift_name.insert(0, "Premium Box")
        row += 1

        # URL изображения
        ttk.Label(input_frame, text="URL изображения:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.gift_image = ttk.Entry(input_frame, width=40)
        self.gift_image.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        self.gift_image.insert(0, "https://i.postimg.cc/jR6TNBW5/Plush-Pepe-Gift.png?dl=1")
        row += 1

        # Количество
        ttk.Label(input_frame, text="Количество:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.gift_quantity = ttk.Entry(input_frame, width=10)
        self.gift_quantity.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        self.gift_quantity.insert(0, "1")
        row += 1

        # Время
        ttk.Label(input_frame, text="Время:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.time_display = ttk.Entry(input_frame, width=10)
        self.time_display.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        self.time_display.insert(0, "24h")
        row += 1

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        generate_btn = ttk.Button(button_frame, text="Сгенерировать карту", command=self.generate_card)
        generate_btn.pack(side=tk.LEFT, padx=5)

        history_btn = ttk.Button(button_frame, text="История запросов", command=self.show_history)
        history_btn.pack(side=tk.LEFT, padx=5)

        # Область для изображения
        self.image_frame = ttk.LabelFrame(main_frame, text="Результат", padding=10)
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.image_label = ttk.Label(self.image_frame, text="Здесь будет сгенерированная карта", background="white")
        self.image_label.pack(expand=True)

        print("✅ Интерфейс создан успешно")

    def init_db(self):
        """Инициализация подключения к БД"""
        try:
            print("🔗 Подключение к MySQL...")
            self.conn = mysql.connector.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            self.cursor = self.conn.cursor()
            print("✅ Успешное подключение к MySQL")

            # Создаем таблицу если не существует
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS gift_card_requests (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp TEXT,
                    primary_color TEXT,
                    secondary_color TEXT,
                    price_usd INT,
                    price_star INT,
                    price_ton INT,
                    gift_name TEXT,
                    gift_image TEXT,
                    gift_quantity INT,
                    time_display TEXT,
                    response_status INT
                )
            ''')
            self.conn.commit()
            print("✅ Таблица создана/проверена")

        except Error as e:
            print(f"❌ Ошибка MySQL: {e}")
            self.fallback_to_sqlite()

    def fallback_to_sqlite(self):
        """Резервное подключение к SQLite"""
        try:
            print("🔗 Подключение к SQLite...")
            self.conn = sqlite3.connect('gift_card_history.db', check_same_thread=False)
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
            print("✅ Успешное подключение к SQLite")
        except Exception as e:
            print(f"❌ Ошибка SQLite: {e}")
            messagebox.showwarning("Предупреждение", "База данных недоступна, но приложение будет работать")

    def generate_card(self):
        """Генерация карты подарка"""
        try:
            print("🎨 Генерация карты...")

            # Собираем данные
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

            print(f"📤 Отправка запроса: {data['gift']['name']}")
            url = "http://localhost:8003/generate_gift_card"
            response = requests.post(url, json=data, timeout=10)

            print(f"📥 Ответ сервера: {response.status_code}")

            # Сохраняем в БД
            self.save_to_db(data, response.status_code)

            if response.status_code == 200:
                # Показываем изображение
                img_data = BytesIO(response.content)
                img = Image.open(img_data)
                img.thumbnail((500, 700))
                photo = ImageTk.PhotoImage(img)

                self.image_label.config(image=photo)
                self.image_label.image = photo

                messagebox.showinfo("Успех", "Карта успешно сгенерирована!")
            else:
                messagebox.showerror("Ошибка", f"Ошибка сервера: {response.status_code}")

        except requests.exceptions.ConnectionError:
            error_msg = "Не удалось подключиться к серверу генерации карт"
            print(f"❌ {error_msg}")
            messagebox.showerror("Ошибка", error_msg)
        except Exception as e:
            error_msg = f"Ошибка: {str(e)}"
            print(f"❌ {error_msg}")
            messagebox.showerror("Ошибка", error_msg)

    def save_to_db(self, data, response_status):
        """Сохранение данных в БД"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"💾 Сохранение в БД...")

            # Универсальный запрос
            query = '''
                INSERT INTO gift_card_requests 
                (timestamp, primary_color, secondary_color, price_usd, price_star, price_ton, 
                 gift_name, gift_image, gift_quantity, time_display, response_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''

            values = (
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
            )

            self.cursor.execute(query, values)
            self.conn.commit()
            print("✅ Данные сохранены в БД")

        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            # Не показываем сообщение об ошибке, чтобы не мешать пользователю

    def show_history(self):
        """Показать историю запросов"""
        try:
            print("📊 Загрузка истории...")

            history_window = tk.Toplevel(self.root)
            history_window.title("История запросов")
            history_window.geometry("900x500")

            # Основной фрейм
            main_frame = ttk.Frame(history_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Treeview
            tree = ttk.Treeview(main_frame, columns=("ID", "Время", "Название", "Статус"), show="headings")
            tree.heading("ID", text="ID")
            tree.heading("Время", text="Время запроса")
            tree.heading("Название", text="Название подарка")
            tree.heading("Статус", text="Статус")

            # Получаем данные
            query = "SELECT id, timestamp, gift_name, response_status FROM gift_card_requests ORDER BY id DESC"
            self.cursor.execute(query)
            records = self.cursor.fetchall()

            print(f"📋 Найдено записей: {len(records)}")

            for record in records:
                status = "✅ Успех" if record[3] == 200 else f"❌ Ошибка {record[3]}"
                tree.insert("", "end", values=(record[0], record[1], record[2], status))

            # Скроллбар
            scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)

            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Кнопки
            button_frame = ttk.Frame(history_window)
            button_frame.pack(pady=10)

            ttk.Button(button_frame, text="Обновить", command=self.show_history).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Закрыть", command=history_window.destroy).pack(side=tk.LEFT, padx=5)

        except Exception as e:
            print(f"❌ Ошибка загрузки истории: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {str(e)}")


# Запуск приложения
if __name__ == "__main__":
    try:
        print("🚀 Запуск приложения...")
        root = tk.Tk()
        app = GiftCardApp(root)
        print("✅ Приложение запущено успешно")
        root.mainloop()
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")