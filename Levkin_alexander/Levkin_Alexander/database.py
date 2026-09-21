import sqlite3
import os
import config

def get_connection():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    db_dir = os.path.dirname(config.DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Users'")
    table_exists = cursor.fetchone() is not None
    conn.close()
    
    if table_exists:
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.executescript('''
        CREATE TABLE Roles (
            RoleID INTEGER PRIMARY KEY AUTOINCREMENT,
            RoleName TEXT NOT NULL UNIQUE
        );
        CREATE TABLE Users (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            RoleID INTEGER NOT NULL,
            FullName TEXT NOT NULL,
            Login TEXT NOT NULL UNIQUE,
            Password TEXT NOT NULL,
            FOREIGN KEY (RoleID) REFERENCES Roles(RoleID)
        );
        CREATE TABLE Categories (
            CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
            CategoryName TEXT NOT NULL UNIQUE
        );
        CREATE TABLE Suppliers (
            SupplierID INTEGER PRIMARY KEY AUTOINCREMENT,
            SupplierName TEXT NOT NULL UNIQUE
        );
        CREATE TABLE Manufacturers (
            ManufacturerID INTEGER PRIMARY KEY AUTOINCREMENT,
            ManufacturerName TEXT NOT NULL UNIQUE
        );
        CREATE TABLE PickupPoints (
            PickupPointID INTEGER PRIMARY KEY AUTOINCREMENT,
            Address TEXT NOT NULL
        );
        CREATE TABLE Products (
            ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
            Article TEXT NOT NULL UNIQUE,
            ProductName TEXT NOT NULL,
            CategoryID INTEGER NOT NULL,
            Description TEXT,
            ManufacturerID INTEGER NOT NULL,
            SupplierID INTEGER NOT NULL,
            Price REAL NOT NULL CHECK (Price >= 0),
            Unit TEXT NOT NULL DEFAULT 'шт.',
            StockQuantity INTEGER NOT NULL DEFAULT 0 CHECK (StockQuantity >= 0),
            Discount INTEGER NOT NULL DEFAULT 0 CHECK (Discount >= 0 AND Discount <= 100),
            ImagePath TEXT,
            FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID),
            FOREIGN KEY (ManufacturerID) REFERENCES Manufacturers(ManufacturerID),
            FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID)
        );
        CREATE TABLE Orders (
            OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
            OrderNumber INTEGER NOT NULL UNIQUE,
            ClientID INTEGER NOT NULL,
            PickupPointID INTEGER NOT NULL,
            OrderDate TEXT NOT NULL,
            DeliveryDate TEXT,
            PickupCode INTEGER NOT NULL,
            Status TEXT NOT NULL,
            FOREIGN KEY (ClientID) REFERENCES Users(UserID),
            FOREIGN KEY (PickupPointID) REFERENCES PickupPoints(PickupPointID)
        );
        CREATE TABLE OrderItems (
            OrderItemID INTEGER PRIMARY KEY AUTOINCREMENT,
            OrderID INTEGER NOT NULL,
            ProductID INTEGER NOT NULL,
            Quantity INTEGER NOT NULL CHECK (Quantity > 0),
            FOREIGN KEY (OrderID) REFERENCES Orders(OrderID) ON DELETE CASCADE,
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID),
            UNIQUE(OrderID, ProductID)
        );
    ''')
    
    cursor.executemany("INSERT INTO Roles (RoleName) VALUES (?)", 
                       [('Администратор',), ('Менеджер',), ('Авторизированный клиент',)])
    cursor.executemany("INSERT INTO Categories (CategoryName) VALUES (?)", 
                       [('Женская обувь',), ('Мужская обувь',)])
    cursor.executemany("INSERT INTO Suppliers (SupplierName) VALUES (?)", 
                       [('Kari',), ('Обувь для вас',)])
    cursor.executemany("INSERT INTO Manufacturers (ManufacturerName) VALUES (?)", 
                       [('Kari',), ('Marco Tozzi',), ('Рос',), ('Rieker',), ('Alessio Nesca',), ('CROSBY',)])
    cursor.executemany("INSERT INTO PickupPoints (Address) VALUES (?)", 
                       [('420151, г. Лесной, ул. Вишневая, 32',), ('125061, г. Лесной, ул. Подгорная, 8',)])
    
    cursor.executemany("INSERT INTO Users (RoleID, FullName, Login, Password) VALUES (?, ?, ?, ?)", [
        (1, 'Никифорова Весения Николаевна', '94d5ous@gmail.com', 'uzWC67'), 
        (2, 'Степанов Михаил Артёмович', '1diph5e@tutanota.com', '8ntwUp'), 
        (3, 'Михайлюк Анна Вячеславовна', '5d4zbu@tutanota.com', 'rwVDh9'), 
        (1, 'Тестовый Админ', 'admin', '123') 
    ])
    
    cursor.executemany('''
        INSERT INTO Products (Article, ProductName, CategoryID, Description, ManufacturerID, SupplierID, Price, Unit, StockQuantity, Discount, ImagePath) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', [
        ('А112Т4', 'Ботинки', 1, 'Женские Ботинки демисезонные kari', 1, 1, 4990.00, 'шт.', 6, 3, '1.jpg'),
        ('F635R4', 'Ботинки', 1, 'Ботинки Marco Tozzi женские демисезонные, размер 39, цвет бежевый', 2, 2, 3244.00, 'шт.', 13, 2, '2.jpg'),
        ('H782T5', 'Туфли', 2, 'Туфли kari мужские классика MYZ21AW-450A, размер 43, цвет: черный', 1, 1, 4499.00, 'шт.', 5, 4, '3.jpg'),
        ('G783F5', 'Ботинки', 2, 'Мужские ботинки Рос-Обувь кожаные с натуральным мехом', 3, 1, 5900.00, 'шт.', 8, 2, '4.jpg'),
        ('J384T6', 'Ботинки', 2, 'B3430/14 Полуботинки мужские Rieker', 4, 2, 3800.00, 'шт.', 16, 2, '5.jpg'),
        ('D572U8', 'Кроссовки', 2, '129615-4 Кроссовки мужские', 3, 2, 4100.00, 'шт.', 6, 3, '6.jpg'),
        ('F572H7', 'Туфли', 1, 'Туфли Marco Tozzi женские летние, размер 39, цвет черный', 2, 1, 2700.00, 'шт.', 14, 2, '7.jpg'),
        ('D329H3', 'Полуботинки', 1, 'Полуботинки Alessio Nesca женские 3-30797-47, размер 37, цвет: бордовый', 5, 2, 1890.00, 'шт.', 4, 4, '8.jpg'),
        ('B320R5', 'Туфли', 1, 'Туфли Rieker женские демисезонные, размер 41, цвет коричневый', 4, 1, 4300.00, 'шт.', 6, 2, '9.jpg'),
        ('G432E4', 'Туфли', 1, 'Туфли kari женские TR-YR-413017, размер 37, цвет: черный', 1, 1, 2800.00, 'шт.', 15, 3, '10.jpg'),
        ('S213E3', 'Полуботинки', 2, '407700/01-01 Полуботинки мужские CROSBY', 6, 2, 2156.00, 'шт.', 6, 3, None),
        ('E482R4', 'Полуботинки', 1, 'Полуботинки kari женские MYZ20S-149, размер 41, цвет: черный', 1, 1, 1800.00, 'шт.', 14, 2, None),
        ('S634B5', 'Кеды', 2, 'Кеды Caprice мужские демисезонные, размер 42, цвет черный', 6, 2, 5500.00, 'шт.', 0, 3, None),
        ('K345R4', 'Полуботинки', 2, '407700/01-02 Полуботинки мужские CROSBY', 6, 2, 2100.00, 'шт.', 3, 2, None),
        ('O754F4', 'Туфли', 1, 'Туфли женские демисезонные Rieker артикул 55073-68/37', 4, 2, 5400.00, 'шт.', 18, 4, None),
        ('G531F4', 'Ботинки', 1, 'Ботинки женские зимние ROMER арт. 893167-01 Черный', 1, 1, 6600.00, 'шт.', 9, 16, None),
        ('J542F5', 'Тапочки', 2, 'Тапочки мужские Арт.70701-55-67син р.41', 1, 1, 500.00, 'шт.', 0, 13, None),
        ('B431R5', 'Ботинки', 2, 'Мужские кожаные ботинки/мужские ботинки', 4, 2, 2700.00, 'шт.', 5, 2, None),
        ('P764G4', 'Туфли', 1, 'Туфли женские, ARGO, размер 38', 6, 1, 6800.00, 'шт.', 15, 15, None),
        ('C436G5', 'Ботинки', 1, 'Ботинки женские, ARGO, размер 40', 5, 1, 10200.00, 'шт.', 9, 15, None),
        ('F427R5', 'Ботинки', 1, 'Ботинки на молнии с декоративной пряжкой FRAU', 4, 2, 11800.00, 'шт.', 11, 15, None),
        ('N457T5', 'Полуботинки', 1, 'Полуботинки Ботинки черные зимние, мех', 6, 1, 4600.00, 'шт.', 13, 3, None),
        ('D364R4', 'Туфли', 1, 'Туфли Luiza Belly женские Kate-lazo черные из натуральной замши', 1, 1, 12400.00, 'шт.', 5, 16, None),
        ('S326R5', 'Тапочки', 2, 'Мужские кожаные тапочки "Профиль С.Дали"', 6, 2, 9900.00, 'шт.', 15, 17, None),
        ('L754R4', 'Полуботинки', 1, 'Полуботинки kari женские WB2020SS-26, размер 38, цвет: черный', 1, 1, 1700.00, 'шт.', 7, 2, None),
        ('M542T5', 'Кроссовки', 2, 'Кроссовки мужские TOFA', 4, 2, 2800.00, 'шт.', 3, 18, None),
        ('D268G5', 'Туфли', 1, 'Туфли Rieker женские демисезонные, размер 36, цвет коричневый', 4, 2, 4399.00, 'шт.', 12, 3, None),
        ('T324F5', 'Сапоги', 1, 'Сапоги замша Цвет: синий', 6, 1, 4699.00, 'шт.', 5, 2, None),
        ('K358H6', 'Тапочки', 2, 'Тапочки мужские син р.41', 4, 1, 599.00, 'шт.', 2, 20, None),
        ('H535R5', 'Ботинки', 1, 'Женские Ботинки демисезонные', 4, 2, 2300.00, 'шт.', 7, 2, None),
    ])
    
    conn.commit()
    conn.close()

def check_login(login, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.UserID, u.FullName, r.RoleName 
        FROM Users u
        JOIN Roles r ON u.RoleID = r.RoleID
        WHERE u.Login = ? AND u.Password = ?
    ''', (login, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user['UserID'],
            'name': user['FullName'],
            'role': user['RoleName']
        }
    return None

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.ProductID, p.Article, p.ProductName, p.Price, p.Discount, 
               p.StockQuantity, p.ImagePath, p.Description, p.Unit,
               s.SupplierName as supplier, c.CategoryName as category,
               m.ManufacturerName as manufacturer
        FROM Products p
        LEFT JOIN Suppliers s ON p.SupplierID = s.SupplierID
        LEFT JOIN Categories c ON p.CategoryID = c.CategoryID
        LEFT JOIN Manufacturers m ON p.ManufacturerID = m.ManufacturerID
        ORDER BY p.ProductName
    ''')
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

def add_product(article, name, category_id, description, manufacturer_id, supplier_id, price, unit, stock_count, discount, photo_path):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Products 
            (Article, ProductName, CategoryID, Description, ManufacturerID, SupplierID, Price, Unit, StockQuantity, Discount, ImagePath)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (article, name, category_id, description, manufacturer_id, supplier_id, price, unit, stock_count, discount, photo_path))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_product(product_id, article, name, category_id, description, manufacturer_id, supplier_id, price, unit, stock_count, discount, photo_path):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Products SET 
            Article=?, ProductName=?, CategoryID=?, Description=?, ManufacturerID=?, 
            SupplierID=?, Price=?, Unit=?, StockQuantity=?, Discount=?, ImagePath=?
        WHERE ProductID=?
    ''', (article, name, category_id, description, manufacturer_id, supplier_id, price, unit, stock_count, discount, photo_path, product_id))
    conn.commit()
    conn.close()

def get_dropdown_data():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT CategoryID, CategoryName FROM Categories")
    categories = {row['CategoryName']: row['CategoryID'] for row in cursor.fetchall()}
    
    cursor.execute("SELECT SupplierID, SupplierName FROM Suppliers")
    suppliers = {row['SupplierName']: row['SupplierID'] for row in cursor.fetchall()}
    
    cursor.execute("SELECT ManufacturerID, ManufacturerName FROM Manufacturers")
    manufacturers = {row['ManufacturerName']: row['ManufacturerID'] for row in cursor.fetchall()}
    
    conn.close()
    return categories, suppliers, manufacturers

def is_product_in_orders(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) as cnt FROM OrderItems WHERE ProductID = ?
    ''', (product_id,))
    result = cursor.fetchone()
    conn.close()
    return result['cnt'] > 0

def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM Products WHERE ProductID = ?', (product_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def get_all_orders():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.OrderID, o.OrderNumber, o.OrderDate, o.DeliveryDate, 
               o.PickupCode, o.Status, u.FullName as client_name,
               pp.Address as pickup_address
        FROM Orders o
        LEFT JOIN Users u ON o.ClientID = u.UserID
        LEFT JOIN PickupPoints pp ON o.PickupPointID = pp.PickupPointID
        ORDER BY o.OrderDate DESC
    ''')
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return orders

def get_order_items(order_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT oi.Quantity, p.ProductName, p.Price, p.Article
        FROM OrderItems oi
        JOIN Products p ON oi.ProductID = p.ProductID
        WHERE oi.OrderID = ?
    ''', (order_id,))
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items

def get_pickup_points():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT PickupPointID, Address FROM PickupPoints")
    points = {row['Address']: row['PickupPointID'] for row in cursor.fetchall()}
    conn.close()
    return points

def get_clients():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT UserID, FullName FROM Users 
        WHERE RoleID = (SELECT RoleID FROM Roles WHERE RoleName = 'Авторизированный клиент')
    ''')
    clients = {row['FullName']: row['UserID'] for row in cursor.fetchall()}
    conn.close()
    return clients

def add_order(order_number, client_id, pickup_point_id, order_date, delivery_date, pickup_code, status, items):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Orders (OrderNumber, ClientID, PickupPointID, OrderDate, DeliveryDate, PickupCode, Status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (order_number, client_id, pickup_point_id, order_date, delivery_date, pickup_code, status))
        order_id = cursor.lastrowid
        for item in items:
            cursor.execute('''
                INSERT INTO OrderItems (OrderID, ProductID, Quantity) VALUES (?, ?, ?)
            ''', (order_id, item['product_id'], item['quantity']))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()

def update_order_status(order_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Orders SET Status = ? WHERE OrderID = ?', (status, order_id))
    conn.commit()
    conn.close()

def delete_order(order_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM OrderItems WHERE OrderID = ?', (order_id,))
        cursor.execute('DELETE FROM Orders WHERE OrderID = ?', (order_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()