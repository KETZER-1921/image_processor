import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import os

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Обработка изображений - Вариант 30")
        self.root.geometry("900x700")

        # Переменные для хранения текущего изображения
        self.current_image = None          # оригинал (BGR)
        self.display_image = None          # для отображения (BGR)
        self.photo = None                  # объект PhotoImage для Tkinter

        # Создаем виджеты
        self.create_widgets()

    def create_widgets(self):
        # Верхняя панель с кнопками
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        ttk.Button(control_frame, text="Загрузить изображение", command=self.load_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Снимок с веб-камеры", command=self.capture_from_camera).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Показать красный канал", command=lambda: self.show_channel('R')).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Показать зеленый канал", command=lambda: self.show_channel('G')).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Показать синий канал", command=lambda: self.show_channel('B')).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Понизить яркость", command=self.adjust_brightness).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Оттенки серого", command=self.to_grayscale).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Нарисовать прямоугольник", command=self.draw_rectangle).pack(side=tk.LEFT, padx=5)

        # Кнопка сброса (показать оригинал)
        ttk.Button(control_frame, text="Сбросить к оригиналу", command=self.reset_to_original).pack(side=tk.LEFT, padx=5)

        # Область для отображения изображения
        self.image_label = ttk.Label(self.root, relief=tk.SUNKEN, anchor=tk.CENTER)
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_label = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X, padx=10, pady=(0,10))

    def load_image(self):
        """Загрузка изображения с диска (PNG или JPG) с расширенной диагностикой"""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg"), ("Все файлы", "*.*")]
        )
        if not file_path:
            return

        try:
            # 1. Проверяем, существует ли файл
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Файл не найден: {file_path}")

            # 2. Проверяем размер файла
            if os.path.getsize(file_path) == 0:
                raise ValueError("Файл пустой (0 байт)")

            # 3. Пытаемся прочитать через OpenCV
            img = cv2.imread(file_path)
            if img is None:
                # Если OpenCV не смог, пробуем через PIL
                try:
                    pil_img = Image.open(file_path)
                    # Конвертируем PIL Image в numpy (RGB) и затем в BGR для OpenCV
                    img_rgb = np.array(pil_img.convert('RGB'))
                    img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
                except Exception as pil_err:
                    raise ValueError(f"Не удалось прочитать файл ни OpenCV, ни PIL. Ошибка PIL: {pil_err}")

            # Сохраняем и отображаем
            self.current_image = img.copy()
            self.display_image = img.copy()
            self.show_image(self.display_image)
            self.status_var.set(f"Загружено: {os.path.basename(file_path)}")

        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))
            self.status_var.set("Ошибка загрузки")

    def capture_from_camera(self):
        """Захват изображения с веб-камеры"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Ошибка", "Не удалось подключиться к веб-камере.\n"
                                           "Возможные решения:\n"
                                           "- Проверьте, что камера подключена и драйверы установлены.\n"
                                           "- Закройте другие приложения, использующие камеру.\n"
                                           "- Попробуйте перезагрузить компьютер.")
            self.status_var.set("Ошибка подключения к камере")
            return

        ret, frame = cap.read()
        cap.release()

        if not ret:
            messagebox.showerror("Ошибка", "Не удалось захватить кадр с камеры.")
            self.status_var.set("Ошибка захвата кадра")
            return

        self.current_image = frame.copy()
        self.display_image = frame.copy()
        self.show_image(self.display_image)
        self.status_var.set("Снимок с веб-камеры сохранен")

    def show_image(self, img_bgr):
        """Отобразить изображение (BGR) в виджете Label"""
        if img_bgr is None:
            return
        # Конвертируем BGR -> RGB для Pillow
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        # Масштабируем с сохранением пропорций
        max_width = 800
        max_height = 550
        # Используем Image.LANCZOS (работает в Pillow 8.x, в новых версиях тоже)
        pil_img.thumbnail((max_width, max_height), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(pil_img)
        self.image_label.config(image=self.photo)
        self.image_label.image = self.photo

    def reset_to_original(self):
        """Показать исходное изображение (без изменений)"""
        if self.current_image is None:
            messagebox.showinfo("Информация", "Сначала загрузите или захватите изображение.")
            return
        self.display_image = self.current_image.copy()
        self.show_image(self.display_image)
        self.status_var.set("Показан оригинал")

    def show_channel(self, channel):
        """Показать один из каналов (R, G, B)"""
        if self.current_image is None:
            messagebox.showinfo("Информация", "Сначала загрузите или захватите изображение.")
            return
        img = self.current_image.copy()
        channel_img = np.zeros_like(img)
        if channel == 'R':
            channel_img[:, :, 2] = img[:, :, 2]  # OpenCV хранит BGR
            self.status_var.set("Показан красный канал")
        elif channel == 'G':
            channel_img[:, :, 1] = img[:, :, 1]
            self.status_var.set("Показан зеленый канал")
        elif channel == 'B':
            channel_img[:, :, 0] = img[:, :, 0]
            self.status_var.set("Показан синий канал")
        else:
            return
        self.display_image = channel_img
        self.show_image(self.display_image)

    def adjust_brightness(self):
        """Понизить яркость на значение, введенное пользователем"""
        if self.current_image is None:
            messagebox.showinfo("Информация", "Сначала загрузите или захватите изображение.")
            return

        value = simpledialog.askinteger("Понижение яркости",
                                        "Введите значение (0-255) для уменьшения яркости:",
                                        minvalue=0, maxvalue=255)
        if value is None:
            return

        img = self.current_image.copy()
        img_int = img.astype(np.int16)
        img_int = np.clip(img_int - value, 0, 255)
        img = img_int.astype(np.uint8)

        self.display_image = img
        self.show_image(self.display_image)
        self.status_var.set(f"Яркость понижена на {value}")

    def to_grayscale(self):
        """Преобразовать изображение в оттенки серого"""
        if self.current_image is None:
            messagebox.showinfo("Информация", "Сначала загрузите или захватите изображение.")
            return

        gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        gray_3ch = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        self.display_image = gray_3ch
        self.show_image(self.display_image)
        self.status_var.set("Изображение преобразовано в оттенки серого")

    def draw_rectangle(self):
        """Нарисовать синий прямоугольник по координатам, введенным пользователем"""
        if self.current_image is None:
            messagebox.showinfo("Информация", "Сначала загрузите или захватите изображение.")
            return

        coords = simpledialog.askstring("Прямоугольник",
                                         "Введите координаты через пробел: x1 y1 x2 y2\n"
                                         "Например: 50 50 200 150")
        if coords is None:
            return
        try:
            parts = list(map(int, coords.split()))
            if len(parts) != 4:
                raise ValueError("Нужно ровно 4 числа")
            x1, y1, x2, y2 = parts
            h, w = self.current_image.shape[:2]
            if x1 < 0 or y1 < 0 or x2 > w or y2 > h or x1 >= x2 or y1 >= y2:
                raise ValueError("Координаты выходят за пределы изображения или заданы некорректно")
        except Exception as e:
            messagebox.showerror("Ошибка ввода", f"Некорректный ввод:\n{str(e)}")
            return

        img = self.current_image.copy()
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), thickness=2)

        self.display_image = img
        self.show_image(self.display_image)
        self.status_var.set(f"Прямоугольник нарисован: ({x1},{y1}) - ({x2},{y2})")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()