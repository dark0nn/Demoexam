import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from PIL import Image
import database
import config

class ProductForm(tk.Toplevel):
    def __init__(self, parent, product_data=None):
        super().__init__(parent)
        self.title("Добавление товара" if not product_data else "Редактирование товара")
        self.geometry(config.FORM_WINDOW_SIZE)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.product_data = product_data
        self.selected_image_path = product_data['ImagePath'] if product_data else None
        
        self.categories, self.suppliers, self.manufacturers = database.get_dropdown_data()
        
        self.create_widgets()
        if self.product_data:
            self.fill_fields()

    def create_widgets(self):
        frame = tk.Frame(self, bg=config.COLOR_BG, padx=20, pady=20)
        frame.pack(fill='both', expand=True)
        
        self.entries = {}
        
        fields = [
            ("Артикул *", "article"), ("Наименование *", "name"), 
            ("Цена *", "price"), ("Количество *", "stock_count"), ("Скидка (%)", "discount"),
            ("Ед. измерения", "unit")
        ]
        
        row = 0
        for label_text, key in fields:
            tk.Label(frame, text=label_text, bg=config.COLOR_BG).grid(row=row, column=0, sticky='w', pady=5)
            entry = tk.Entry(frame, width=30)
            entry.grid(row=row, column=1, pady=5)
            self.entries[key] = entry
            row += 1
            
        tk.Label(frame, text="Категория *", bg=config.COLOR_BG).grid(row=row, column=0, sticky='w', pady=5)
        self.category_combo = ttk.Combobox(frame, values=list(self.categories.keys()), state="readonly", width=28)
        self.category_combo.grid(row=row, column=1, pady=5)
        row += 1
        
        tk.Label(frame, text="Поставщик *", bg=config.COLOR_BG).grid(row=row, column=0, sticky='w', pady=5)
        self.supplier_combo = ttk.Combobox(frame, values=list(self.suppliers.keys()), state="readonly", width=28)
        self.supplier_combo.grid(row=row, column=1, pady=5)
        row += 1
        
        tk.Label(frame, text="Производитель *", bg=config.COLOR_BG).grid(row=row, column=0, sticky='w', pady=5)
        self.manufacturer_combo = ttk.Combobox(frame, values=list(self.manufacturers.keys()), state="readonly", width=28)
        self.manufacturer_combo.grid(row=row, column=1, pady=5)
        row += 1
        
        tk.Label(frame, text="Описание", bg=config.COLOR_BG).grid(row=row, column=0, sticky='w', pady=5)
        self.entries["description"] = tk.Text(frame, width=30, height=4)
        self.entries["description"].grid(row=row, column=1, pady=5)
        row += 1
        
        tk.Label(frame, text="Фото товара", bg=config.COLOR_BG).grid(row=row, column=0, sticky='w', pady=5)
        photo_frame = tk.Frame(frame, bg=config.COLOR_BG)
        photo_frame.grid(row=row, column=1, pady=5, sticky='w')
        
        tk.Button(photo_frame, text="Выбрать фото", command=self.choose_image).pack(side='left')
        self.photo_label = tk.Label(photo_frame, text="Не выбрано", bg=config.COLOR_BG, fg="gray")
        self.photo_label.pack(side='left', padx=10)
        row += 1
        
        btn_frame = tk.Frame(frame, bg=config.COLOR_BG)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="Сохранить", command=self.save_product, 
                  bg=config.COLOR_ACCENT, fg="white", width=15).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Отмена", command=self.destroy, 
                  bg=config.COLOR_SECONDARY, fg=config.COLOR_ACCENT, width=15).pack(side='left', padx=10)

    def choose_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if filepath:
            img = Image.open(filepath)
            img.thumbnail((config.PHOTO_WIDTH, config.PHOTO_HEIGHT), Image.Resampling.LANCZOS)
            
            filename = os.path.basename(filepath)
            save_path = os.path.join(config.IMG_DIR, filename)
            img.save(save_path)
            
            self.selected_image_path = filename
            self.photo_label.config(text=filename, fg="black")

    def fill_fields(self):
        p = self.product_data
        self.entries["article"].insert(0, p['Article'])
        self.entries["article"].config(state='disabled')
        self.entries["name"].insert(0, p['ProductName'])
        self.entries["price"].insert(0, p['Price'])
        self.entries["stock_count"].insert(0, p['StockQuantity'])
        self.entries["discount"].insert(0, p['Discount'])
        self.entries["unit"].insert(0, p['Unit'])
        self.entries["description"].insert('1.0', p['Description'] or "")
        
        self.category_combo.set(p['category'])
        self.supplier_combo.set(p['supplier'])
        self.manufacturer_combo.set(p['manufacturer'])
        
        if p['ImagePath']:
            self.selected_image_path = p['ImagePath']
            self.photo_label.config(text=p['ImagePath'], fg="black")

    def save_product(self):
        article = self.entries["article"].get().strip()
        name = self.entries["name"].get().strip()
        
        if not article or not name or not self.category_combo.get():
            messagebox.showerror("Ошибка", "Заполните обязательные поля (отмечены *)")
            return
            
        try:
            price = float(self.entries["price"].get())
            stock = int(self.entries["stock_count"].get())
            discount = float(self.entries["discount"].get() or 0)
            
            if price < 0 or stock < 0 or discount < 0 or discount > 100:
                messagebox.showerror("Ошибка", "Цена и количество не могут быть отрицательными. Скидка: 0-100%")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Цена, количество и скидка должны быть числами")
            return

        data = {
            'article': article,
            'name': name,
            'category_id': self.categories[self.category_combo.get()],
            'supplier_id': self.suppliers[self.supplier_combo.get()],
            'manufacturer_id': self.manufacturers[self.manufacturer_combo.get()],
            'price': price,
            'stock_count': stock,
            'discount': discount,
            'unit': self.entries["unit"].get().strip() or 'шт.',
            'description': self.entries["description"].get('1.0', tk.END).strip(),
            'photo_path': self.selected_image_path
        }

        if self.product_data:
            database.update_product(self.product_data['ProductID'], **data)
            messagebox.showinfo("Успех", "Товар обновлен!")
        else:
            if not database.add_product(**data):
                messagebox.showerror("Ошибка", "Товар с таким артикулом уже существует!")
                return
            messagebox.showinfo("Успех", "Товар добавлен!")
            
        self.destroy()