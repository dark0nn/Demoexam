import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import database
import config

class OrdersWindow(tk.Toplevel):
    def __init__(self, parent, role):
        super().__init__(parent)
        self.title("Управление заказами")
        self.geometry("900x600")
        self.transient(parent)
        self.grab_set()
        self.role = role
        
        self.create_widgets()
        self.load_orders()

    def create_widgets(self):
        top_frame = tk.Frame(self, bg=config.COLOR_BG)
        top_frame.pack(fill='x', padx=10, pady=5)
        
        if self.role == config.ROLE_ADMIN:
            tk.Button(top_frame, text="Новый заказ", command=self.add_order,
                      bg=config.COLOR_ACCENT, fg="white").pack(side='left', padx=5)
        
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('number', 'client', 'date', 'delivery', 'code', 'status', 'pickup')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('number', text='Номер')
        self.tree.heading('client', text='Клиент')
        self.tree.heading('date', text='Дата заказа')
        self.tree.heading('delivery', text='Дата доставки')
        self.tree.heading('code', text='Код получения')
        self.tree.heading('status', text='Статус')
        self.tree.heading('pickup', text='Пункт выдачи')
        
        self.tree.column('number', width=60)
        self.tree.column('client', width=180)
        self.tree.column('date', width=90)
        self.tree.column('delivery', width=90)
        self.tree.column('code', width=80)
        self.tree.column('status', width=80)
        self.tree.column('pickup', width=250)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.tree.bind('<<TreeviewSelect>>', self.show_order_details)
        
        self.detail_text = tk.Text(self, height=8, bg=config.COLOR_BG)
        self.detail_text.pack(fill='x', padx=10, pady=5)
        
        if self.role == config.ROLE_ADMIN:
            btn_frame = tk.Frame(self, bg=config.COLOR_BG)
            btn_frame.pack(fill='x', padx=10, pady=5)
            
            tk.Button(btn_frame, text="Изменить статус", command=self.change_status,
                      bg=config.COLOR_ACCENT, fg="white").pack(side='left', padx=5)
            tk.Button(btn_frame, text="Удалить заказ", command=self.delete_order,
                      bg="#FF6B6B", fg="white").pack(side='left', padx=5)

    def load_orders(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        orders = database.get_all_orders()
        self.orders_data = {o['OrderID']: o for o in orders}
        
        for order in orders:
            self.tree.insert('', 'end', iid=order['OrderID'], values=(
                order['OrderNumber'], order['client_name'], order['OrderDate'],
                order['DeliveryDate'], order['PickupCode'], order['Status'],
                order['pickup_address']
            ))

    def show_order_details(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        order_id = int(selected[0])
        items = database.get_order_items(order_id)
        
        self.detail_text.delete('1.0', tk.END)
        self.detail_text.insert(tk.END, "Состав заказа:\n")
        total = 0
        for item in items:
            line = f"  {item['Article']} - {item['ProductName']} x{item['Quantity']} = {item['Price'] * item['Quantity']:.2f} руб.\n"
            self.detail_text.insert(tk.END, line)
            total += item['Price'] * item['Quantity']
        self.detail_text.insert(tk.END, f"\nИтого: {total:.2f} руб.")

    def change_status(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ!")
            return
        
        order_id = int(selected[0])
        
        win = tk.Toplevel(self)
        win.title("Изменить статус")
        win.geometry("300x150")
        
        tk.Label(win, text="Новый статус:").pack(pady=5)
        status_combo = ttk.Combobox(win, values=["Новый", "Завершен", "Отменён"], state="readonly")
        status_combo.pack(pady=5)
        
        def save():
            if status_combo.get():
                database.update_order_status(order_id, status_combo.get())
                messagebox.showinfo("Успех", "Статус обновлён!")
                self.load_orders()
                win.destroy()
        
        tk.Button(win, text="Сохранить", command=save).pack(pady=10)

    def delete_order(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ!")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить этот заказ?"):
            order_id = int(selected[0])
            database.delete_order(order_id)
            messagebox.showinfo("Успех", "Заказ удалён!")
            self.load_orders()

    def add_order(self):
        win = tk.Toplevel(self)
        win.title("Новый заказ")
        win.geometry("400x400")
        
        clients = database.get_clients()
        pickup_points = database.get_pickup_points()
        products = database.get_all_products()
        
        tk.Label(win, text="Клиент:").pack()
        client_combo = ttk.Combobox(win, values=list(clients.keys()), state="readonly")
        client_combo.pack()
        
        tk.Label(win, text="Пункт выдачи:").pack()
        pickup_combo = ttk.Combobox(win, values=list(pickup_points.keys()), state="readonly")
        pickup_combo.pack()
        
        tk.Label(win, text="Дата доставки (ГГГГ-ММ-ДД):").pack()
        delivery_entry = tk.Entry(win)
        delivery_entry.insert(0, str(date.today()))
        delivery_entry.pack()
        
        tk.Label(win, text="Товар:").pack()
        product_names = [f"{p['Article']} - {p['ProductName']}" for p in products]
        product_combo = ttk.Combobox(win, values=product_names, state="readonly")
        product_combo.pack()
        
        tk.Label(win, text="Количество:").pack()
        qty_entry = tk.Entry(win)
        qty_entry.insert(0, "1")
        qty_entry.pack()
        
        def save():
            if not client_combo.get() or not pickup_combo.get() or not product_combo.get():
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return
            try:
                qty = int(qty_entry.get())
                if qty <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Ошибка", "Количество должно быть положительным числом!")
                return
            
            import random
            order_number = random.randint(1000, 9999)
            pickup_code = random.randint(100, 999)
            
            selected_product_name = product_combo.get()
            product_id = None
            for p in products:
                if f"{p['Article']} - {p['ProductName']}" == selected_product_name:
                    product_id = p['ProductID']
                    break
            
            items = [{'product_id': product_id, 'quantity': qty}]
            
            if database.add_order(
                order_number, clients[client_combo.get()],
                pickup_points[pickup_combo.get()],
                str(date.today()), delivery_entry.get(),
                pickup_code, "Новый", items
            ):
                messagebox.showinfo("Успех", f"Заказ #{order_number} создан! Код получения: {pickup_code}")
                self.load_orders()
                win.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать заказ!")
        
        tk.Button(win, text="Создать заказ", command=save, bg=config.COLOR_ACCENT, fg="white").pack(pady=15)