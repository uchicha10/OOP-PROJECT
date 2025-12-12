import customtkinter as ctk
from tkinter import ttk


def setup_queue_tab(app):
    """Setup order queue tab"""
    queue_frame = ctk.CTkFrame(app.queue_tab)
    queue_frame.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("Customer", "Order", "Service", "Packaging", "Status")
    app.queue_tree = ttk.Treeview(
        queue_frame, columns=columns, show="headings", height=15)

    for col in columns:
        app.queue_tree.heading(col, text=col)
        app.queue_tree.column(col, width=150, anchor="center")

    scrollbar = ttk.Scrollbar(
        queue_frame, orient="vertical", command=app.queue_tree.yview)
    app.queue_tree.configure(yscrollcommand=scrollbar.set)
    app.queue_tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    control_frame = ctk.CTkFrame(app.queue_tab)
    control_frame.pack(fill="x", padx=10, pady=10)

    ctk.CTkButton(
        control_frame, text="👨‍🍳 Prepare Next Order",
        command=app.prepare_next_order, width=200
    ).pack(side="left", padx=5)

    ctk.CTkButton(
        control_frame, text="🍽️ Serve Order",
        command=app.serve_order, width=200
    ).pack(side="left", padx=5)

    ctk.CTkButton(
        control_frame, text="🔄 Refresh Queue",
        command=app.update_queue_display, width=200
    ).pack(side="left", padx=5)
