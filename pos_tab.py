import customtkinter as ctk
from tkinter import ttk


def setup_pos_tab(app):
    """Setup Point of Sale tab"""
    main_pos_frame = ctk.CTkFrame(app.pos_tab)
    main_pos_frame.pack(fill="both", expand=True, padx=10, pady=10)

    left_frame = ctk.CTkFrame(main_pos_frame, width=200)
    left_frame.pack(side="left", fill="y", padx=(0, 5), pady=5)
    left_frame.pack_propagate(False)

    ctk.CTkLabel(left_frame, text="CATEGORIES",
                 font=("Arial", 16, "bold"),
                 text_color="#8B4513").pack(pady=12)

    categories = [
        ("☕ Coffee", "Coffee"),
        ("🍰 Sweet Treats", "Sweet Treats"),
        ("🍵 Tea", "Tea"),
        ("🔥 Hot Drinks", "Hot Beverages"),
        ("❄️ Cold Drinks", "Cold Beverages"),
        ("🥪 Food", "Food"),
    ]

    app.category_buttons = []
    for display_name, category in categories:
        btn = ctk.CTkButton(
            left_frame,
            text=display_name,
            font=("Arial", 12, "bold"),
            height=45,
            fg_color="#f8f8f8",
            text_color="#333333",
            hover_color="#e8e8e8",
            border_width=2,
            border_color="#dddddd",
            anchor="w",
            command=lambda c=category: app.select_category(c)
        )
        btn.pack(fill="x", padx=8, pady=4)
        app.category_buttons.append((btn, category))

    right_frame = ctk.CTkFrame(main_pos_frame)
    right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0), pady=5)

    top_section = ctk.CTkFrame(right_frame)
    top_section.pack(fill="both", expand=True, pady=(0, 5))

    app.products_header = ctk.CTkLabel(
        top_section, text="COFFEE",
        font=("Arial", 20, "bold"),
        text_color="#8B4513"
    )
    app.products_header.pack(pady=8)

    products_container = ctk.CTkFrame(top_section)
    products_container.pack(fill="both", expand=True, padx=10, pady=5)

    app.products_canvas = ctk.CTkCanvas(
        products_container, bg="#f0f0f0", highlightthickness=0)
    scrollbar = ttk.Scrollbar(
        products_container, orient="vertical", command=app.products_canvas.yview)
    app.products_scrollable_frame = ctk.CTkFrame(app.products_canvas)

    app.products_scrollable_frame.bind(
        "<Configure>",
        lambda e: app.products_canvas.configure(
            scrollregion=app.products_canvas.bbox("all"))
    )

    app.products_canvas.create_window(
        (0, 0), window=app.products_scrollable_frame, anchor="nw")
    app.products_canvas.configure(yscrollcommand=scrollbar.set)
    app.products_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    bottom_section = ctk.CTkFrame(right_frame, height=350)
    bottom_section.pack(fill="x", pady=(5, 0))
    bottom_section.pack_propagate(False)

    bottom_tabview = ctk.CTkTabview(bottom_section)
    bottom_tabview.pack(fill="both", expand=True, padx=5, pady=5)

    options_tab = bottom_tabview.add("🛍️ Product Options")

    app.selected_product_frame = ctk.CTkFrame(options_tab, height=60)
    app.selected_product_frame.pack(fill="x", padx=5, pady=5)
    app.selected_product_frame.pack_propagate(False)

    options_main_frame = ctk.CTkFrame(options_tab)
    options_main_frame.pack(fill="both", expand=True, padx=5, pady=5)

    left_options = ctk.CTkFrame(options_main_frame)
    left_options.pack(side="left", fill="both", expand=True, padx=5)

    middle_options = ctk.CTkFrame(options_main_frame)
    middle_options.pack(side="left", fill="both", expand=True, padx=5)

    right_options = ctk.CTkFrame(options_main_frame)
    right_options.pack(side="right", fill="both", expand=True, padx=5)

    size_frame = ctk.CTkFrame(left_options)
    size_frame.pack(fill="x", pady=5)

    ctk.CTkLabel(size_frame, text="Size Options:",
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=2)

    app.size_var = ctk.StringVar(value="Regular")
    for size in ["Regular", "Large"]:
        ctk.CTkRadioButton(
            size_frame, text=size, variable=app.size_var, value=size
        ).pack(anchor="w", pady=1)

    app.temp_frame = ctk.CTkFrame(left_options)
    app.temp_frame.pack(fill="x", pady=5)

    ctk.CTkLabel(app.temp_frame, text="Temperature:",
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=2)

    app.temp_var = ctk.StringVar(value="Hot")
    for temp in ["Hot", "Iced"]:
        ctk.CTkRadioButton(
            app.temp_frame, text=temp, variable=app.temp_var, value=temp
        ).pack(anchor="w", pady=1)

    addons_frame = ctk.CTkFrame(middle_options)
    addons_frame.pack(fill="both", expand=True, pady=5)

    ctk.CTkLabel(addons_frame, text="Add-ons (Optional):",
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=2)

    app.addons_container = ctk.CTkScrollableFrame(
        addons_frame, height=120, border_width=2, border_color="#dddddd")
    app.addons_container.pack(fill="both", expand=True, pady=2)

    action_frame = ctk.CTkFrame(right_options)
    action_frame.pack(fill="both", expand=True, pady=5)

    ctk.CTkLabel(action_frame, text="Order Actions:",
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=2)

    ctk.CTkButton(
        action_frame, text="➕ Add to Cart",
        command=app.add_to_cart,
        width=140, fg_color="#8B4513", height=35
    ).pack(pady=5)

    ctk.CTkButton(
        action_frame, text="🔄 Clear Selection",
        command=app.clear_selection,
        width=140, height=35
    ).pack(pady=5)

    ctk.CTkButton(
        action_frame, text="📋 View Cart",
        command=lambda: bottom_tabview.set("🛒 Shopping Cart"),
        width=140, height=35, fg_color="#2e8b57"
    ).pack(pady=5)

    cart_tab = bottom_tabview.add("🛒 Shopping Cart")

    cart_tree_frame = ctk.CTkFrame(cart_tab)
    cart_tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

    cart_columns = ("Item", "Size", "Temp", "Add-ons", "Price")
    app.cart_tree = ttk.Treeview(
        cart_tree_frame, columns=cart_columns, show="headings", height=6)

    column_widths = {"Item": 180, "Size": 70, "Temp": 70,
                     "Add-ons": 150, "Price": 80}
    for col in cart_columns:
        app.cart_tree.heading(col, text=col)
        app.cart_tree.column(col, width=column_widths.get(col, 100), anchor="center")

    cart_scrollbar = ttk.Scrollbar(
        cart_tree_frame, orient="vertical", command=app.cart_tree.yview)
    app.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
    app.cart_tree.pack(side="left", fill="both", expand=True)
    cart_scrollbar.pack(side="right", fill="y")

    cart_summary_frame = ctk.CTkFrame(cart_tab)
    cart_summary_frame.pack(fill="x", padx=5, pady=5)

    app.cart_total_label = ctk.CTkLabel(
        cart_summary_frame, text="Total: ₱0.00", font=("Arial", 14, "bold"))
    app.cart_total_label.pack(side="left", padx=10)

    cart_buttons = ctk.CTkFrame(cart_tab)
    cart_buttons.pack(fill="x", padx=5, pady=5)

    ctk.CTkButton(
        cart_buttons, text="🗑️ Remove Selected",
        command=app.remove_from_cart,
        width=140
    ).pack(side="left", padx=5)

    ctk.CTkButton(
        cart_buttons, text="🧹 Clear Cart",
        command=app.clear_cart,
        width=120
    ).pack(side="left", padx=5)

    ctk.CTkButton(
        cart_buttons, text="💳 Checkout Order",
        command=app.checkout,
        width=140, fg_color="#2e8b57"
    ).pack(side="left", padx=5)

    ctk.CTkLabel(
        app.selected_product_frame,
        text="Select a product from the menu",
        font=("Arial", 12)
    ).pack(pady=10)

    app.select_category("Coffee")
