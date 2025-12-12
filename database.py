import sqlite3
import os
from PIL import Image, ImageDraw

DB_FILE = "cafe_shop.db"
IMAGES_DIR = "product_images"


def create_default_image():
    """Create a default product image"""
    default_path = os.path.join(IMAGES_DIR, "default.jpg")
    if not os.path.exists(default_path):
        img = Image.new('RGB', (300, 300), color="#B26464")
        draw = ImageDraw.Draw(img)

        cup_color = '#8B4513'
        coffee_color = '#4B3621'
        steam_color = '#666666'

        draw.ellipse([80, 180, 220, 220], fill=cup_color, outline='#000000', width=2)
        draw.rectangle([80, 120, 220, 180], fill=cup_color, outline='#000000', width=2)
        draw.ellipse([90, 170, 210, 210], fill=coffee_color)
        draw.arc([220, 140, 240, 160], 270, 90, fill=cup_color, width=8)

        for i, (y_start, y_end) in enumerate([(100, 90), (110, 95), (120, 100)]):
            draw.line([150 + i * 10, y_start, 150 + i * 10, y_end], fill=steam_color, width=2)

        draw.text((150, 250), "Default Product", fill='#333333', anchor="mm")
        img.save(default_path, 'JPEG', quality=90)
        print("Default image created!")


def init_db():
    """Initialize database with default data"""
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)

    create_default_image()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS sales_history")
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS addons")
    cursor.execute("DROP TABLE IF EXISTS menu")

    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_number VARCHAR(20),
            order_name VARCHAR(255),
            add_ons VARCHAR(255),
            size VARCHAR(20),
            temperature VARCHAR(20),
            service_type VARCHAR(20),
            packaging_type VARCHAR(20),
            total DECIMAL(10,2),
            status VARCHAR(50),
            order_time DATETIME
        )
    """)

    cursor.execute("""
        CREATE TABLE menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) UNIQUE,
            category VARCHAR(50),
            subcategory VARCHAR(50),
            price DECIMAL(10,2),
            stock INTEGER DEFAULT 100,
            image_path VARCHAR(255),
            is_available BOOLEAN DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE addons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255),
            category VARCHAR(50),
            price DECIMAL(10,2),
            stock INTEGER DEFAULT 100,
            is_available BOOLEAN DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE sales_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            customer_number VARCHAR(20),
            product_name VARCHAR(255),
            addon_name VARCHAR(255),
            quantity INTEGER,
            unit_price DECIMAL(10,2),
            total_price DECIMAL(10,2),
            service_type VARCHAR(20),
            packaging_type VARCHAR(20),
            sale_time DATETIME,
            FOREIGN KEY (order_id) REFERENCES orders (id)
        )
    """)

    default_menu = [
        ("Espresso", "Coffee", "Hot Coffee", 60, 100, "espresso.jpg"),
        ("Americano", "Coffee", "Hot Coffee", 70, 100, "americano.jpg"),
        ("Latte", "Coffee", "Hot Coffee", 80, 100, "latte.jpg"),
        ("Cappuccino", "Coffee", "Hot Coffee", 80, 100, "cappuccino.jpg"),
        ("Mocha", "Coffee", "Hot Coffee", 90, 100, "mocha.jpg"),
        ("Flat White", "Coffee", "Hot Coffee", 85, 100, "flat_white.jpg"),
        ("Iced Americano", "Coffee", "Cold Coffee", 75, 100, "iced_americano.jpg"),
        ("Iced Latte", "Coffee", "Cold Coffee", 85, 100, "iced_latte.jpg"),
        ("Iced Mocha", "Coffee", "Cold Coffee", 95, 100, "iced_mocha.jpg"),
        ("Cold Brew", "Coffee", "Cold Coffee", 80, 100, "cold_brew.jpg"),
        ("Frappuccino", "Coffee", "Cold Coffee", 120, 100, "frappuccino.jpg"),

        ("Chocolate Muffin", "Sweet Treats", "Pastry", 40, 30, "chocolate_muffin.jpg"),
        ("Blueberry Muffin", "Sweet Treats", "Pastry", 45, 30, "blueberry_muffin.jpg"),
        ("Croissant", "Sweet Treats", "Pastry", 35, 30, "croissant.jpg"),
        ("Chocolate Chip Cookie", "Sweet Treats", "Pastry", 25, 30, "cookie.jpg"),
        ("Brownie", "Sweet Treats", "Pastry", 50, 30, "brownie.jpg"),

        ("Black Tea", "Tea", "Hot Tea", 50, 100, "black_tea.jpg"),
        ("Green Tea", "Tea", "Hot Tea", 50, 100, "green_tea.jpg"),
        ("Earl Grey", "Tea", "Hot Tea", 55, 100, "earl_grey.jpg"),
        ("Chamomile", "Tea", "Hot Tea", 55, 100, "chamomile.jpg"),
        ("English Breakfast", "Tea", "Hot Tea", 60, 100, "english_breakfast.jpg"),
        ("Iced Tea", "Tea", "Cold Tea", 55, 100, "iced_tea.jpg"),
        ("Iced Green Tea", "Tea", "Cold Tea", 55, 100, "iced_green_tea.jpg"),
        ("Iced Lemon Tea", "Tea", "Cold Tea", 60, 100, "iced_lemon_tea.jpg"),
        ("Peach Iced Tea", "Tea", "Cold Tea", 65, 100, "peach_iced_tea.jpg"),

        ("Hot Chocolate", "Hot Beverages", "Hot Drinks", 65, 100, "hot_chocolate.jpg"),
        ("Matcha Latte", "Hot Beverages", "Hot Drinks", 95, 100, "matcha_latte.jpg"),
        ("Turmeric Latte", "Hot Beverages", "Hot Drinks", 85, 100, "turmeric_latte.jpg"),

        ("Bubble Tea", "Cold Beverages", "Cold Drinks", 120, 100, "bubble_tea.jpg"),
        ("Coke Float", "Cold Beverages", "Cold Drinks", 75, 10, "coke_float.jpg"),

        ("Ham Sandwich", "Food", "Sandwich", 60, 50, "ham_sandwich.jpg"),
        ("Chicken Sandwich", "Food", "Sandwich", 65, 50, "chicken_sandwich.jpg"),
        ("Veggie Sandwich", "Food", "Sandwich", 55, 50, "veggie_sandwich.jpg"),
        ("Club Sandwich", "Food", "Sandwich", 80, 50, "club_sandwich.jpg"),
        ("Grilled Cheese", "Food", "Sandwich", 50, 50, "grilled_cheese.jpg"),
    ]

    for name, category, subcategory, price, stock, image in default_menu:
        image_path = os.path.join(IMAGES_DIR, image)
        if not os.path.exists(image_path):
            image_path = os.path.join(IMAGES_DIR, "default.jpg")
        cursor.execute(
            "INSERT INTO menu (name, category, subcategory, price, stock, image_path) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, category, subcategory, price, stock, image_path)
        )

    default_addons = [
        ("Extra Shot", "Coffee", 15, 100),
        ("Whipped Cream", "Coffee", 10, 100),
        ("Caramel Syrup", "Coffee", 15, 100),
        ("Chocolate Syrup", "Coffee", 15, 100),
        ("Vanilla Syrup", "Coffee", 15, 100),
        ("Hazelnut Syrup", "Coffee", 15, 100),
        ("Honey", "Tea", 5, 100),
        ("Lemon", "Tea", 5, 100),
        ("Mint", "Tea", 5, 100),
        ("Ginger", "Tea", 5, 100),
        ("Extra Cheese", "Food", 10, 100),
        ("Bacon", "Food", 15, 100),
        ("Avocado", "Food", 20, 100),
        ("Extra Scoop", "Cold Beverages", 15, 50),
        ("Tapioca Pearls", "Cold Beverages", 10, 100),
    ]

    for name, category, price, stock in default_addons:
        cursor.execute(
            "INSERT INTO addons (name, category, price, stock) VALUES (?, ?, ?, ?)",
            (name, category, price, stock)
        )

    conn.commit()
    conn.close()
    print("Database initialized successfully!")


def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DB_FILE)
