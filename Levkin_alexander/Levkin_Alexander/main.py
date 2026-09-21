import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
import database
import config
from product_form import ProductForm
from orders_window import OrdersWindow

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        database.init_db()
        self.title(config.APP_TITLE)
        self.geometry(config.MAIN_WINDOW_SIZE)
        self.configure(bg=config.COLOR_BG)
        
        self.current_user_role = config.ROLE_GUEST
        self.current_user_name = config.ROLE_GUEST
        self.images_cache = {}
        self.all_products = []
        
        self.show_login_screen()

    def show_login_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        frame = tk.Frame(self, bg=config.COLOR_BG)
        frame.pack(expand=True)
        
        tk.Label(frame, text="Логин:", bg=config.COLOR_BG, font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL)).grid(row=0, column=0, pady=5)
        self.entry_login = tk.Entry(frame, font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL))
        self.entry_login.grid(row=0, column=1, pady=5)
        
        tk.Label(frame, text="Пароль:", bg=config.COLOR_BG, font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL)).grid(row=1, column=0, pady=5)
        self.entry_pass = tk.Entry(frame, show="*", font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL))
        self.entry_pass.grid(row=1, column=1, pady=5)
        
        btn_login = tk.Button(frame, text="Войти", command=self.login, 
                              bg=config.COLOR_ACCENT, fg="white", font=(config.FONT_FAMILY, config.FONT_SIZE_BOLD, "bold"))
        btn_login.grid(row=2, column=0, pady=15, padx=5)
        
        btn_guest = tk.Button(frame, text="Гость", command=lambda: self.start_app(config.ROLE_GUEST, config.ROLE_GUEST),
                              bg=config.COLOR_SECONDARY, fg=config.COLOR_ACCENT, font=(config.FONT_FAMILY, config.FONT_SIZE_BOLD, "bold"))
        btn_guest.grid(row=2, column=1, pady=15, padx=5)

    def login(self):
        login_text = self.entry_login.get().strip()
        password_text = self.entry_pass.get().strip()
        
        if not login_text or not password_text:
            messagebox.showwarning("Ошибка", "Введите логин и пароль!")
            return
            
        user = database.check_login(login_text, password_text)
        
        if user:
            self.start_app(user['role'], user['name'])
            self.entry_pass.delete(0, tk.END)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")

    def start_app(self, role, name):
        self.current_user_role = role
        self.current_user_name = name
        self.show_main_screen()

    def logout(self):
        self.current_user_role = config.ROLE_GUEST
        self.current_user_name = config.ROLE_GUEST
        self.show_login_screen()

    def show_main_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        top_frame = tk.Frame(self, bg=config.COLOR_BG)
        top_frame.pack(fill='x', padx=10, pady=5)
        
        btn_logout = tk.Button(top_frame, text="Выход", command=self.logout,
                               bg=config.COLOR_SECONDARY, fg=config.COLOR_ACCENT,
                               font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold"))
        btn_logout.pack(side='left')
        
        tk.Label(top_frame, text=f"{self.current_user_name} ({self.current_user_role})", 
                 font=(config.FONT_FAMILY, config.FONT_SIZE_TITLE, "bold"), 
                 bg=config.COLOR_BG, fg=config.COLOR_ACCENT).pack(side='right')
        
        if self.current_user_role in [config.ROLE_MANAGER, config.ROLE_ADMIN]:
            control_frame = tk.Frame(self, bg=config.COLOR_BG)
            control_frame.pack(fill='x', padx=10, pady=5)
            
            tk.Label(control_frame, text="Поиск:", bg=config.COLOR_BG).pack(side='left')
            self.search_var = tk.StringVar()
            self.search_var.trace_add('write', self.apply_filters)
            tk.Entry(control_frame, textvariable=self.search_var, width=20).pack(side='left', padx=5)
            
            tk.Label(control_frame, text="Поставщик:", bg=config.COLOR_BG).pack(side='left')
            self.supplier_combo = ttk.Combobox(control_frame, values=["Все поставщики"], state="readonly", width=15)
            self.supplier_combo.set("Все поставщики")
            self.supplier_combo.pack(side='left', padx=5)
            self.supplier_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
            
            tk.Label(control_frame, text="Сортировка:", bg=config.COLOR_BG).pack(side='left')
            self.sort_combo = ttk.Combobox(control_frame, 
                                            values=["По умолчанию", "По возрастанию", "По убыванию"], 
                                            state="readonly", width=15)
            self.sort_combo.set("По умолчанию")
            self.sort_combo.pack(side='left', padx=5)
            self.sort_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())

        self.canvas = tk.Canvas(self, bg=config.COLOR_BG, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=config.COLOR_BG)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        if self.current_user_role in [config.ROLE_ADMIN, config.ROLE_MANAGER]:
            btn_frame = tk.Frame(self, bg=config.COLOR_BG)
            btn_frame.pack(fill='x', padx=10, pady=5)
            tk.Button(btn_frame, text="Заказы", command=self.open_orders,
                      bg=config.COLOR_ACCENT, fg="white", font=(config.FONT_FAMILY, config.FONT_SIZE_BOLD, "bold")).pack(side='left', padx=5)
            
        if self.current_user_role == config.ROLE_ADMIN:
            if 'btn_frame' not in locals():
                btn_frame = tk.Frame(self, bg=config.COLOR_BG)
                btn_frame.pack(fill='x', padx=10, pady=5)
            tk.Button(btn_frame, text="Добавить товар", command=self.open_add_product,
                      bg=config.COLOR_ACCENT, fg="white", font=(config.FONT_FAMILY, config.FONT_SIZE_BOLD, "bold")).pack(side='left', padx=5)
            
        self.load_products()

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def load_products(self):
        products = database.get_all_products()
        self.all_products = products
        
        if self.current_user_role in [config.ROLE_MANAGER, config.ROLE_ADMIN]:
            suppliers = ["Все поставщики"] + list(set(p['supplier'] for p in products if p['supplier']))
            self.supplier_combo['values'] = suppliers
            
        self.display_products(products)

    def display_products(self, products):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        for product in products:
            self.create_product_card(product)
        
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_product_card(self, product):
        bg_color = config.COLOR_BG
        if product['StockQuantity'] == 0:
            bg_color = config.COLOR_OUT_OF_STOCK
        elif product['Discount'] > 15:
            bg_color = config.COLOR_HIGH_DISCOUNT
            
        card = tk.Frame(self.scrollable_frame, bg=bg_color, bd=1, relief='solid')
        card.pack(fill='x', padx=10, pady=5)
        
        if self.current_user_role == config.ROLE_ADMIN:
            card.bind('<Button-1>', lambda e, p=product: self.open_edit_product(p))
        
        img_path = config.DEFAULT_IMAGE
        if product['ImagePath']:
            test_path = os.path.join(config.IMG_DIR, product['ImagePath'])
            if os.path.exists(test_path):
                img_path = test_path

        try:
            img = Image.open(img_path)
            img = img.resize((120, 120), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            lbl_photo = tk.Label(card, image=photo, bg=bg_color)
            lbl_photo.image = photo 
            lbl_photo.pack(side='left', padx=10, pady=10)
            if self.current_user_role == config.ROLE_ADMIN:
                lbl_photo.bind('<Button-1>', lambda e, p=product: self.open_edit_product(p))
        except Exception:
            lbl_photo = tk.Label(card, text="[Нет фото]", width=15, height=6, bg="#ccc")
            lbl_photo.pack(side='left', padx=10, pady=10)
            if self.current_user_role == config.ROLE_ADMIN:
                lbl_photo.bind('<Button-1>', lambda e, p=product: self.open_edit_product(p))
        
        info_frame = tk.Frame(card, bg=bg_color)
        info_frame.pack(side='left', fill='x', expand=True, padx=5, pady=10)
        if self.current_user_role == config.ROLE_ADMIN:
            info_frame.bind('<Button-1>', lambda e, p=product: self.open_edit_product(p))
        
        tk.Label(info_frame, text=product['ProductName'], font=(config.FONT_FAMILY, config.FONT_SIZE_BOLD, "bold"), bg=bg_color).pack(anchor='w')
        tk.Label(info_frame, text=f"Артикул: {product['Article']}", font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL), bg=bg_color).pack(anchor='w')
        tk.Label(info_frame, text=f"Категория: {product['category']}", font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL), bg=bg_color).pack(anchor='w')
        tk.Label(info_frame, text=f"Поставщик: {product['supplier']}", font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL), bg=bg_color).pack(anchor='w')
        
        if product['Discount'] > 0:
            old_price = product['Price'] / (1 - product['Discount']/100)
            tk.Label(info_frame, text=f"{old_price:.2f} руб.", fg=config.COLOR_RED, font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "underline"), bg=bg_color).pack(anchor='w')
            tk.Label(info_frame, text=f"{product['Price']:.2f} руб.", fg=config.COLOR_BLACK, font=(config.FONT_FAMILY, config.FONT_SIZE_BOLD, "bold"), bg=bg_color).pack(anchor='w')
        else:
            tk.Label(info_frame, text=f"{product['Price']:.2f} руб.", fg=config.COLOR_BLACK, font=(config.FONT_FAMILY, config.FONT_SIZE_BOLD, "bold"), bg=bg_color).pack(anchor='w')
            
        stock_text = "НЕТ В НАЛИЧИИ" if product['StockQuantity'] == 0 else f"Остаток: {product['StockQuantity']} {product['Unit']}"
        stock_color = config.COLOR_RED if product['StockQuantity'] == 0 else config.COLOR_BLACK
        tk.Label(info_frame, text=stock_text, fg=stock_color, font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold"), bg=bg_color).pack(anchor='w')
        
        if self.current_user_role == config.ROLE_ADMIN:
            btn_frame = tk.Frame(card, bg=bg_color)
            btn_frame.pack(side='right', padx=10)
            tk.Button(btn_frame, text="Удалить", 
                      command=lambda p=product: self.delete_product(p),
                      bg="#FF6B6B", fg="white", 
                      font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, "bold")).pack()

    def apply_filters(self, *args):
        search_text = self.search_var.get().lower()
        selected_supplier = self.supplier_combo.get()
        sort_type = self.sort_combo.get()
        
        filtered = []
        for p in self.all_products:
            matches_search = (
                search_text in p['ProductName'].lower() or 
                search_text in p['Article'].lower() or
                search_text in str(p['Price']).lower() or
                search_text in (p.get('category') or '').lower() or
                search_text in (p.get('supplier') or '').lower() or
                search_text in (p.get('Description') or '').lower()
            )
            matches_supplier = (selected_supplier == "Все поставщики") or (p['supplier'] == selected_supplier)
            
            if matches_search and matches_supplier:
                filtered.append(p)
                
        if sort_type == "По возрастанию":
            filtered.sort(key=lambda x: x['StockQuantity'])
        elif sort_type == "По убыванию":
            filtered.sort(key=lambda x: x['StockQuantity'], reverse=True)
                
        self.display_products(filtered)

    def open_add_product(self):
        form = ProductForm(self, product_data=None)
        self.wait_window(form)
        self.load_products()

    def open_edit_product(self, product):
        form = ProductForm(self, product_data=product)
        self.wait_window(form)
        self.load_products()

    def open_orders(self):
        OrdersWindow(self, self.current_user_role)

    def delete_product(self, product):
        if not messagebox.askyesno("Подтверждение", f"Удалить товар '{product['ProductName']}'?"):
            return
            
        if database.is_product_in_orders(product['ProductID']):
            messagebox.showerror("Ошибка", "Невозможно удалить товар, который присутствует в заказе!")
            return
            
        if database.delete_product(product['ProductID']):
            messagebox.showinfo("Успех", "Товар удалён!")
            self.load_products()
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить товар!")

if __name__ == "__main__":
    app = App()
    app.mainloop()