# cafe_system.py
import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk
from collections import deque
from datetime import datetime
import sqlite3
import os
from database import get_db_connection
from image_manager import ImageManager

# Database and image configuration
DB_FILE = "cafe_shop.db"
IMAGES_DIR = "product_images"

class CafeShopSystem:
    """Main café management system"""
    def __init__(self, root):
        self.root = root
        self.root.title("☕ BrewVerse Café System")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)

        # Center the window
        self.root.eval('tk::PlaceWindow . center')

        # Initialize variables
        self.customer_number = 1
        self.order_queue = deque()
        self.cart_items = []
        self.current_addons = []
        self.service_type = ctk.StringVar(value="Dine-in")
        self.packaging_type = ctk.StringVar(value="Standard")
        self.product_images = {}  # Dictionary to store product images
        self.image_manager = ImageManager(IMAGES_DIR)  # Initialize image manager
        self.current_image_path = None

        self.setup_ui()

    def setup_ui(self):
        """Setup the main user interface"""
        # Main title
        title_frame = ctk.CTkFrame(self.root)
        title_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(title_frame, 
                    text="☕ Welcome to BrewVerse Café ☕", 
                    font=("Arial", 24, "bold")).pack(pady=15)

        # Service Type Selection
        service_frame = ctk.CTkFrame(self.root)
        service_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(service_frame, text="Service Type:", 
                    font=("Arial", 14, "bold")).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(service_frame, text="Dine-in", 
                          variable=self.service_type, 
                          value="Dine-in").pack(side="left", padx=10)
        
        ctk.CTkRadioButton(service_frame, text="Take-out", 
                          variable=self.service_type, 
                          value="Take-out",
                          command=self.on_takeout_selected).pack(side="left", padx=10)

        # Packaging Type Selection (only visible for take-out)
        self.packaging_frame = ctk.CTkFrame(self.root)
        ctk.CTkLabel(self.packaging_frame, text="Packaging:", 
                    font=("Arial", 14, "bold")).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(self.packaging_frame, text="Standard", 
                          variable=self.packaging_type, 
                          value="Standard").pack(side="left", padx=5)
        
        ctk.CTkRadioButton(self.packaging_frame, text="Premium", 
                          variable=self.packaging_type, 
                          value="Premium").pack(side="left", padx=5)

        # Create tabs for different sections
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Menu Management Tab
        self.menu_tab = self.tabview.add("📋 Menu Management")
        self.setup_menu_tab()
        
        # POS Tab
        self.pos_tab = self.tabview.add("💰 Point of Sale")
        self.setup_pos_tab()
        
        # Order Queue Tab
        self.queue_tab = self.tabview.add("📊 Order Queue")
        self.setup_queue_tab()

    def setup_menu_tab(self):
        """Setup menu management tab"""
        # Menu treeview
        tree_frame = ctk.CTkFrame(self.menu_tab)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("ID", "Name", "Category", "Subcategory", "Price", "Stock", "Status", "Image")
        self.menu_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        column_widths = {"ID": 50, "Name": 150, "Category": 100, "Subcategory": 120, 
                        "Price": 80, "Stock": 80, "Status": 100, "Image": 150}
        for col in columns:
            self.menu_tree.heading(col, text=col)
            self.menu_tree.column(col, width=column_widths.get(col, 100), anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.menu_tree.yview)
        self.menu_tree.configure(yscrollcommand=scrollbar.set)
        
        self.menu_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Control buttons frame
        control_frame = ctk.CTkFrame(self.menu_tab)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Input fields
        input_frame = ctk.CTkFrame(control_frame)
        input_frame.pack(fill="x", pady=5)
        
        # Name
        ctk.CTkLabel(input_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.menu_name_entry = ctk.CTkEntry(input_frame, width=150)
        self.menu_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Category
        ctk.CTkLabel(input_frame, text="Category:").grid(row=0, column=2, padx=5, pady=5)
        self.menu_category_combobox = ctk.CTkComboBox(input_frame, 
                                                    values=["Coffee", "Tea", "Food", "Special"],
                                                    width=150)
        self.menu_category_combobox.grid(row=0, column=3, padx=5, pady=5)
        
        # Subcategory
        ctk.CTkLabel(input_frame, text="Subcategory:").grid(row=0, column=4, padx=5, pady=5)
        self.menu_subcategory_combobox = ctk.CTkComboBox(input_frame, 
                                                       values=["Hot Coffee", "Cold Coffee", "Hot Tea", "Cold Tea", 
                                                              "Sandwich", "Pastry", "Special Drink"],
                                                       width=150)
        self.menu_subcategory_combobox.grid(row=0, column=5, padx=5, pady=5)
        
        # Price
        ctk.CTkLabel(input_frame, text="Price:").grid(row=0, column=6, padx=5, pady=5)
        self.menu_price_entry = ctk.CTkEntry(input_frame, width=100)
        self.menu_price_entry.grid(row=0, column=7, padx=5, pady=5)
        
        # Stock
        ctk.CTkLabel(input_frame, text="Stock:").grid(row=0, column=8, padx=5, pady=5)
        self.menu_stock_entry = ctk.CTkEntry(input_frame, width=100)
        self.menu_stock_entry.grid(row=0, column=9, padx=5, pady=5)
        
        # Image upload section
        image_frame = ctk.CTkFrame(control_frame)
        image_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(image_frame, text="Product Image:").grid(row=0, column=0, padx=5, pady=5)
        self.image_path_label = ctk.CTkLabel(image_frame, text="No image selected", 
                                           width=300, anchor="w")
        self.image_path_label.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        
        ctk.CTkButton(image_frame, text="📁 Upload Image", 
                     command=self.upload_product_image, 
                     width=120).grid(row=0, column=3, padx=5, pady=5)
        
        ctk.CTkButton(image_frame, text="🗑️ Clear Image", 
                     command=self.clear_product_image, 
                     width=120,
                     fg_color="#b22222").grid(row=0, column=4, padx=5, pady=5)
        
        # Current image preview
        self.image_preview_label = ctk.CTkLabel(image_frame, text="Preview will appear here", 
                                               width=100, height=100)
        self.image_preview_label.grid(row=1, column=0, columnspan=5, padx=5, pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(control_frame)
        button_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(button_frame, text="➕ Add Product", 
                      command=self.add_product).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="✏️ Update Product", 
                      command=self.update_product).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="🗑️ Delete Product", 
                      command=self.delete_product).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="📦 Restock", 
                      command=self.restock_product).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="🔄 Refresh", 
                      command=self.load_menu).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="📊 Sales Report", 
                      command=self.show_sales_report,
                      fg_color="#2e8b57").pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="🚪 Logout", 
                      command=self.logout,
                      fg_color="#b45f06").pack(side="left", padx=5)
        
        # Bind tree selection
        self.menu_tree.bind('<<TreeviewSelect>>', self.on_menu_selection)
        
        # Load initial data
        self.load_menu()

    def setup_pos_tab(self):
        """Setup Point of Sale tab with McDonald's style layout"""
        # Main frame for POS
        main_pos_frame = ctk.CTkFrame(self.pos_tab)
        main_pos_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - Categories (like McDonald's sidebar)
        left_frame = ctk.CTkFrame(main_pos_frame, width=250)
        left_frame.pack(side="left", fill="y", padx=(0, 5), pady=5)
        left_frame.pack_propagate(False)
        
        # Categories title
        ctk.CTkLabel(left_frame, text="CATEGORIES", 
                    font=("Arial", 18, "bold"), 
                    text_color="#2e8b57").pack(pady=15)
        
        # Category buttons (like McDonald's sidebar)
        categories = [
            ("☕ Coffee", "Coffee"),
            ("🍵 Tea", "Tea"), 
            ("🥪 Food", "Food"),
            ("⭐ Special", "Special")
        ]
        
        self.category_buttons = []
        for display_name, category in categories:
            btn = ctk.CTkButton(
                left_frame,
                text=display_name,
                font=("Arial", 14, "bold"),
                height=50,
                fg_color="#f8f8f8",
                text_color="#333333",
                hover_color="#e8e8e8",
                border_width=2,
                border_color="#dddddd",
                anchor="w",
                command=lambda c=category: self.select_category(c)
            )
            btn.pack(fill="x", padx=10, pady=5)
            self.category_buttons.append((btn, category))
        
        # Right side - Products display
        right_frame = ctk.CTkFrame(main_pos_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0), pady=5)
        
        # Products header
        self.products_header = ctk.CTkLabel(right_frame, text="COFFEE", 
                                          font=("Arial", 20, "bold"),
                                          text_color="#2e8b57")
        self.products_header.pack(pady=10)
        
        # Products display frame with scrollbar
        products_container = ctk.CTkFrame(right_frame)
        products_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create a canvas and scrollbar for products
        self.products_canvas = ctk.CTkCanvas(products_container, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(products_container, orient="vertical", command=self.products_canvas.yview)
        self.products_scrollable_frame = ctk.CTkFrame(self.products_canvas)
        
        self.products_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.products_canvas.configure(scrollregion=self.products_canvas.bbox("all"))
        )
        
        self.products_canvas.create_window((0, 0), window=self.products_scrollable_frame, anchor="nw")
        self.products_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.products_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bottom section - Cart and options
        bottom_frame = ctk.CTkFrame(right_frame)
        bottom_frame.pack(fill="x", padx=10, pady=10)
        
        # Selected product info
        self.selected_product_frame = ctk.CTkFrame(bottom_frame)
        self.selected_product_frame.pack(fill="x", pady=5)
        
        # Options frame
        options_frame = ctk.CTkFrame(bottom_frame)
        options_frame.pack(fill="x", pady=5)
        
        # Size options
        ctk.CTkLabel(options_frame, text="Size:", 
                    font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        
        self.size_var = ctk.StringVar(value="Regular")
        sizes = ["Regular", "Large"]
        
        size_frame = ctk.CTkFrame(options_frame)
        size_frame.pack(fill="x", pady=5)
        
        for size in sizes:
            ctk.CTkRadioButton(size_frame, text=size, 
                              variable=self.size_var, 
                              value=size).pack(side="left", padx=5)
        
        # Temperature options (only for drinks)
        self.temp_frame = ctk.CTkFrame(options_frame)
        ctk.CTkLabel(self.temp_frame, text="Temperature:", 
                    font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        
        self.temp_var = ctk.StringVar(value="Hot")
        temps = ["Hot", "Cold", "Iced"]
        
        temp_inner_frame = ctk.CTkFrame(self.temp_frame)
        temp_inner_frame.pack(fill="x", pady=5)
        
        for temp in temps:
            ctk.CTkRadioButton(temp_inner_frame, text=temp, 
                              variable=self.temp_var, 
                              value=temp).pack(side="left", padx=5)
        
        # Add-ons frame
        addons_frame = ctk.CTkFrame(bottom_frame)
        addons_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(addons_frame, text="Add-ons (Optional):", 
                    font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        
        self.addons_container = ctk.CTkFrame(addons_frame)
        self.addons_container.pack(fill="x", padx=10, pady=5)
        
        # Cart frame
        cart_frame = ctk.CTkFrame(bottom_frame)
        cart_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(cart_frame, text="🛒 Shopping Cart", 
                    font=("Arial", 16, "bold")).pack(pady=10)
        
        # Cart treeview
        cart_columns = ("Item", "Size", "Temp", "Add-ons", "Price")
        self.cart_tree = ttk.Treeview(cart_frame, columns=cart_columns, show="headings", height=6)
        
        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=100, anchor="center")
        
        cart_scrollbar = ttk.Scrollbar(cart_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        
        self.cart_tree.pack(side="left", fill="both", expand=True)
        cart_scrollbar.pack(side="right", fill="y")
        
        # Cart buttons
        cart_buttons = ctk.CTkFrame(cart_frame)
        cart_buttons.pack(fill="x", pady=10)
        
        ctk.CT