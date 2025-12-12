import customtkinter as ctk
from tkinter import ttk


def setup_menu_tab(app):
    """Setup menu management tab with organized category view"""
    main_frame = ctk.CTkFrame(app.menu_tab)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    left_frame = ctk.CTkFrame(main_frame, width=250)
    left_frame.pack(side="left", fill="y", padx=(0, 5), pady=5)
    left_frame.pack_propagate(False)

    ctk.CTkLabel(left_frame, text="FILTER BY CATEGORY",
                 font=("Arial", 16, "bold"),
                 text_color="#8B4513").pack(pady=12)

    categories = [
        ("☕ All Products", "All"),
        ("☕ Coffee", "Coffee"),
        ("🍰 Sweet Treats", "Sweet Treats"),
        ("🍵 Tea", "Tea"),
        ("🔥 Hot Beverages", "Hot Beverages"),
        ("❄️ Cold Beverages", "Cold Beverages"),
        ("🥪 Food", "Food"),
    ]

    app.category_filter_buttons = []
    for display_name, category in categories:
        btn = ctk.CTkButton(
            left_frame,
            text=display_name,
            font=("Arial", 12, "bold"),
            height=45,
            fg_color="#915c5c",
            text_color="#333333",
            hover_color="#e8e8e8",
            border_width=2,
            border_color="#dddddd",
            anchor="w",
            command=lambda c=category: app.filter_menu_by_category(c)
        )
        btn.pack(fill="x", padx=8, pady=4)
        app.category_filter_buttons.append((btn, category))

    ctk.CTkLabel(left_frame, text="FILTER BY SUBCATEGORY",
                 font=("Arial", 14, "bold"),
                 text_color="#8B4513").pack(pady=(20, 5))

    subcategories = [
        "All Subcategories",
        "Hot Coffee", "Cold Coffee",
        "Pastry",
        "Hot Tea", "Cold Tea",
        "Hot Drinks", "Cold Drinks",
        "Sandwich",
    ]

    app.current_filter_category = "All"
    app.current_filter_subcategory = "All Subcategories"

    app.subcategory_var = ctk.StringVar(value="All Subcategories")
    app.subcategory_combobox = ctk.CTkComboBox(
        left_frame,
        values=subcategories,
        variable=app.subcategory_var,
        command=app.filter_menu_by_subcategory,
        width=200,
    )
    app.subcategory_combobox.pack(pady=5)

    ctk.CTkLabel(left_frame, text="SEARCH PRODUCTS",
                 font=("Arial", 14, "bold"),
                 text_color="#8B4513").pack(pady=(20, 5))

    search_frame = ctk.CTkFrame(left_frame)
    search_frame.pack(fill="x", padx=5, pady=5)

    app.search_entry = ctk.CTkEntry(
        search_frame, placeholder_text="Search by name...")
    app.search_entry.pack(fill="x", padx=5, pady=5)
    app.search_entry.bind('<KeyRelease>', app.search_products)

    right_frame = ctk.CTkFrame(main_frame)
    right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0), pady=5)

    tree_frame = ctk.CTkFrame(right_frame)
    tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

    columns = ("ID", "Name", "Category", "Subcategory",
               "Price", "Stock", "Status", "Image")
    app.menu_tree = ttk.Treeview(
        tree_frame, columns=columns, show="headings", height=15)

    column_widths = {
        "ID": 50, "Name": 150, "Category": 100, "Subcategory": 120,
        "Price": 80, "Stock": 80, "Status": 100, "Image": 150
    }
    for col in columns:
        app.menu_tree.heading(col, text=col)
        app.menu_tree.column(col, width=column_widths.get(col, 100), anchor="center")

    scrollbar = ttk.Scrollbar(
        tree_frame, orient="vertical", command=app.menu_tree.yview)
    app.menu_tree.configure(yscrollcommand=scrollbar.set)
    app.menu_tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    control_frame = ctk.CTkFrame(right_frame)
    control_frame.pack(fill="x", padx=5, pady=5)

    input_frame = ctk.CTkFrame(control_frame)
    input_frame.pack(fill="x", pady=5)

    ctk.CTkLabel(input_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
    app.menu_name_entry = ctk.CTkEntry(input_frame, width=150)
    app.menu_name_entry.grid(row=0, column=1, padx=5, pady=5)

    ctk.CTkLabel(input_frame, text="Category:").grid(row=0, column=2, padx=5, pady=5)
    app.menu_category_combobox = ctk.CTkComboBox(
        input_frame,
        values=["Coffee", "Sweet Treats", "Tea",
                "Hot Beverages", "Cold Beverages", "Food"],
        width=150,
    )
    app.menu_category_combobox.grid(row=0, column=3, padx=5, pady=5)

    ctk.CTkLabel(input_frame, text="Subcategory:").grid(row=0, column=4, padx=5, pady=5)
    app.menu_subcategory_combobox = ctk.CTkComboBox(
        input_frame,
        values=["Hot Coffee", "Cold Coffee", "Pastry",
                "Hot Tea", "Cold Tea", "Hot Drinks",
                "Cold Drinks", "Sandwich"],
        width=150,
    )
    app.menu_subcategory_combobox.grid(row=0, column=5, padx=5, pady=5)

    ctk.CTkLabel(input_frame, text="Price:").grid(row=1, column=0, padx=5, pady=5)
    app.menu_price_entry = ctk.CTkEntry(input_frame, width=100)
    app.menu_price_entry.grid(row=1, column=1, padx=5, pady=5)

    ctk.CTkLabel(input_frame, text="Stock:").grid(row=1, column=2, padx=5, pady=5)
    app.menu_stock_entry = ctk.CTkEntry(input_frame, width=100)
    app.menu_stock_entry.grid(row=1, column=3, padx=5, pady=5)

    image_frame = ctk.CTkFrame(control_frame)
    image_frame.pack(fill="x", pady=5)

    ctk.CTkLabel(image_frame, text="Product Image:").grid(
        row=0, column=0, padx=5, pady=5)
    app.image_path_label = ctk.CTkLabel(
        image_frame, text="No image selected", width=300, anchor="w")
    app.image_path_label.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

    ctk.CTkButton(
        image_frame, text="📁 Upload Image",
        command=app.upload_product_image,
        width=120
    ).grid(row=0, column=3, padx=5, pady=5)

    ctk.CTkButton(
        image_frame, text="🗑️ Clear Image",
        command=app.clear_product_image,
        width=120, fg_color="#b22222"
    ).grid(row=0, column=4, padx=5, pady=5)

    app.image_preview_label = ctk.CTkLabel(
        image_frame, text="Preview will appear here",
        width=100, height=100
    )
    app.image_preview_label.grid(row=1, column=0, columnspan=5, padx=5, pady=10)

    button_frame = ctk.CTkFrame(control_frame)
    button_frame.pack(fill="x", pady=5)

    ctk.CTkButton(button_frame, text="➕ Add Product",
                  command=app.add_product).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="✏️ Update Product",
                  command=app.update_product).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="🗑️ Delete Product",
                  command=app.delete_product).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="📦 Restock",
                  command=app.restock_product).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="🔄 Refresh",
                  command=app.load_menu).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="📊 Sales Report",
                  command=app.show_sales_report,
                  fg_color="#2e8b57").pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="📦 Sales Inventory",
                  command=app.show_sales_inventory,
                  fg_color="#8B4513").pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="🚪 Logout",
                  command=app.logout,
                  fg_color="#b45f06").pack(side="left", padx=5)

    app.menu_tree.bind('<<TreeviewSelect>>', app.on_menu_selection)
    app.load_menu()
