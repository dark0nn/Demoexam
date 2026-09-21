import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'db', 'store.db')
IMG_DIR = os.path.join(BASE_DIR, 'img')
DEFAULT_IMAGE = os.path.join(IMG_DIR, 'picture.png')

COLOR_BG = "#FFFFFF"            
COLOR_HIGH_DISCOUNT = "#2E8B57" 
COLOR_OUT_OF_STOCK = "#87CEEB"  
COLOR_ACCENT = "#546F94"       
COLOR_SECONDARY = "#ABCFCE"     
COLOR_RED = "#FF0000"           
COLOR_BLACK = "#000000"         

FONT_FAMILY = "Arial"
FONT_SIZE_NORMAL = 10
FONT_SIZE_BOLD = 11
FONT_SIZE_TITLE = 14

PHOTO_WIDTH = 300
PHOTO_HEIGHT = 200

ROLE_GUEST = "Гость"
ROLE_CLIENT = "Авторизированный клиент"
ROLE_MANAGER = "Менеджер"
ROLE_ADMIN = "Администратор"

APP_TITLE = "Магазин Обуви"
LOGIN_WINDOW_SIZE = "400x300"
MAIN_WINDOW_SIZE = "1000x700"
FORM_WINDOW_SIZE = "500x600"