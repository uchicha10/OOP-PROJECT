import customtkinter as ctk
import os
import sqlite3
from tkinter import messagebox, ttk
from collections import deque
from datetime import datetime

from database import init_db, get_db_connection, IMAGES_DIR
from image_manager import ImageManager
from menu_tab import setup_menu_tab
from pos_tab import setup_pos_tab
from queue_tab import setup_queue_tab
from login import LoginWindow

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")


class CafeShopSystem:
    """Main café management system"""

    def __init__(self, root):
        self.root = root
        self.root.title("☕ BrewVerse Café System")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        self.root.eval('tk::PlaceWindow . center')

        self.customer_number = 1
        self.order_queue = []
        self.cart_items = []
        self.current_addons = []
        self.service_type = ctk.StringVar(value="Dine-in")
        self.packaging_type = ctk.StringVar(value="Standard")
        self.product_images = {}
        self.image_manager = ImageManager(IMAGES_DIR)
        self.current_image_path = None

        self.setup_ui()

    def setup_ui(self):
        title_frame = ctk.CTkFrame(self.root)
        title_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            title_frame,
            text="☕ Welcome to BrewVerse Café ☕",
            font=("Arial", 24, "bold")
        ).pack(pady=15)

        service_frame = ctk.CTkFrame(self.root)
        service_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            service_frame,
            text="Service Type:",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=10)

        ctk.CTkRadioButton(
            service_frame,
            text="Dine-in",
            variable=self.service_type,
            value="Dine-in"
        ).pack(side="right", padx=10)

        ctk.CTkRadioButton(
            service_frame,
            text="Take-out",
            variable=self.service_type,
            value="Take-out",
            command=self.on_takeout_selected
        ).pack(side="right", padx=10)

        self.packaging_frame = ctk.CTkFrame(self.root)

        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.menu_tab = self.tabview.add("📋 Menu Management")
        self.pos_tab = self.tabview.add("💰 Point of Sale")
        self.queue_tab = self.tabview.add("📊 Order Queue")

        setup_menu_tab(self)
        setup_pos_tab(self)
        setup_queue_tab(self)

    # ===== Filters & Menu loading =====

    def filter_menu_by_category(self, category):
        self.current_filter_category = category
        for btn, btn_category in self.category_filter_buttons:
            if btn_category == category:
                btn.configure(fg_color="#8B4513", text_color="white")
            else:
                btn.configure(fg_color="#f8f8f8", text_color="#333333")
        self.apply_filters()

    def filter_menu_by_subcategory(self, subcategory):
        self.current_filter_subcategory = subcategory
        self.apply_filters()

    def search_products(self, event=None):
        self.apply_filters()

    def apply_filters(self):
        search_term = self.search_entry.get().strip().lower()
        for item in self.menu_tree.get_children():
            self.menu_tree.delete(item)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = "SELECT id, name, category, subcategory, price, stock, image_path FROM menu WHERE 1=1"
            params = []

            if self.current_filter_category != "All":
                query += " AND category = ?"
                params.append(self.current_filter_category)

            if self.current_filter_subcategory != "All Subcategories":
                query += " AND subcategory = ?"
                params.append(self.current_filter_subcategory)

            if search_term:
                query += " AND LOWER(name) LIKE ?"
                params.append(f"%{search_term}%")

            query += " ORDER BY category, subcategory, name"

            cursor.execute(query, params)
            for row in cursor.fetchall():
                item_id, name, category, subcategory, price, stock, image_path = row
                status = "Available" if stock > 0 else "Sold Out"
                image_name = os.path.basename(image_path) if image_path else "No image"
                self.menu_tree.insert(
                    "",
                    "end",
                    values=(item_id, name, category, subcategory,
                            f"₱{price}", stock, status, image_name)
                )
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading menu: {e}")
        finally:
            conn.close()

    # ===== POS / selection / cart =====

    def clear_selection(self):
        if hasattr(self, 'selected_product'):
            del self.selected_product
        if hasattr(self, 'selected_subcategory'):
            del self.selected_subcategory

        for widget in self.selected_product_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.selected_product_frame,
            text="Select a product from the menu",
            font=("Arial", 12)
        ).pack(pady=10)

        for widget in self.addons_container.winfo_children():
            widget.destroy()

        self.size_var.set("Regular")
        self.temp_var.set("Hot")
        self.temp_frame.pack_forget()

    def select_category(self, category):
        category_names = {
            "Coffee": "COFFEE",
            "Sweet Treats": "SWEET TREATS",
            "Tea": "TEA",
            "Hot Beverages": "HOT BEVERAGES",
            "Cold Beverages": "COLD BEVERAGES",
            "Food": "FOOD",
        }
        self.products_header.configure(text=category_names.get(category, category.upper()))

        for btn, btn_category in self.category_buttons:
            if btn_category == category:
                btn.configure(fg_color="#8B4513", text_color="white")
            else:
                btn.configure(fg_color="#f8f8f8", text_color="#333333")

        self.current_category = category
        self.load_products_by_category(category)

    def load_products_by_category(self, category):
        for widget in self.products_scrollable_frame.winfo_children():
            widget.destroy()

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT name, price, stock, image_path, subcategory "
                "FROM menu WHERE category=? AND stock > 0 "
                "ORDER BY subcategory, name",
                (category,)
            )
            products = cursor.fetchall()

            if products:
                row = 0
                col = 0
                max_cols = 3
                for name, price, stock, image_path, subcategory in products:
                    product_card = ctk.CTkFrame(
                        self.products_scrollable_frame, width=220, height=260)
                    product_card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
                    product_card.grid_propagate(False)

                    try:
                        photo = self.image_manager.get_image_preview(image_path, size=(140, 100))
                        image_label = ctk.CTkLabel(product_card, image=photo, text="")
                        image_label.pack(pady=6)
                        if name not in self.product_images:
                            self.product_images[name] = photo
                    except Exception:
                        icon = (
                            "☕" if category == "Coffee" else
                            "🍰" if category == "Sweet Treats" else
                            "🍵" if category == "Tea" else
                            "🔥" if category == "Hot Beverages" else
                            "❄️" if category == "Cold Beverages" else "🥪"
                        )
                        ctk.CTkLabel(product_card, text=icon, font=("Arial", 35)).pack(pady=12)

                    ctk.CTkLabel(
                        product_card, text=name,
                        font=("Arial", 13, "bold"),
                        wraplength=200
                    ).pack(pady=2)

                    ctk.CTkLabel(
                        product_card, text=subcategory,
                        font=("Arial", 10), text_color="#666666"
                    ).pack(pady=1)

                    ctk.CTkLabel(
                        product_card, text=f"₱{price}",
                        font=("Arial", 12, "bold"),
                        text_color="#8B4513"
                    ).pack(pady=1)

                    ctk.CTkLabel(
                        product_card, text=f"Stock: {stock}",
                        font=("Arial", 10), text_color="#666666"
                    ).pack(pady=1)

                    ctk.CTkButton(
                        product_card, text="SELECT", width=180,
                        fg_color="#8B4513", hover_color="#A0522D",
                        command=lambda n=name, sc=subcategory: self.select_product(n, sc)
                    ).pack(pady=6)

                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
            else:
                ctk.CTkLabel(
                    self.products_scrollable_frame,
                    text=f"No {category.lower()} products available",
                    font=("Arial", 16)
                ).pack(pady=50)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading products: {e}")
        finally:
            conn.close()

        self.selected_product = None
        self.update_selected_product_info()

    def select_product(self, product_name, subcategory):
        self.selected_product = product_name
        self.selected_subcategory = subcategory
        self.update_selected_product_info()
        self.load_addons()

    def update_selected_product_info(self):
        for widget in self.selected_product_frame.winfo_children():
            widget.destroy()

        if hasattr(self, 'selected_product') and self.selected_product:
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "SELECT name, price, image_path, stock FROM menu WHERE name=?",
                    (self.selected_product,)
                )
                product = cursor.fetchone()
                if product:
                    name, price, image_path, stock = product

                    if any(x in self.selected_subcategory for x in ["Coffee", "Tea", "Drinks"]):
                        self.temp_frame.pack(fill="x", pady=5)
                    else:
                        self.temp_frame.pack_forget()

                    info_frame = ctk.CTkFrame(self.selected_product_frame)
                    info_frame.pack(fill="both", expand=True, padx=5, pady=5)

                    try:
                        photo = self.image_manager.get_image_preview(image_path, size=(45, 45))
                        image_label = ctk.CTkLabel(info_frame, image=photo, text="")
                        image_label.pack(side="left", padx=8)
                        if f"selected_{name}" not in self.product_images:
                            self.product_images[f"selected_{name}"] = photo
                    except Exception:
                        icon = (
                            "☕" if "Coffee" in self.selected_subcategory else
                            "🍰" if "Sweet Treats" in self.current_category else
                            "🍵" if "Tea" in self.selected_subcategory else
                            "🔥" if "Hot" in self.selected_subcategory else
                            "❄️" if "Cold" in self.selected_subcategory else "🥪"
                        )
                        ctk.CTkLabel(info_frame, text=icon, font=("Arial", 18)).pack(side="left", padx=8)

                    details_frame = ctk.CTkFrame(info_frame)
                    details_frame.pack(side="left", fill="both", expand=True, padx=8)

                    ctk.CTkLabel(
                        details_frame,
                        text=f"Selected: {name}",
                        font=("Arial", 12, "bold")
                    ).grid(row=0, column=0, sticky="w", pady=1)

                    ctk.CTkLabel(
                        details_frame,
                        text=f"Price: ₱{price}",
                        font=("Arial", 11)
                    ).grid(row=1, column=0, sticky="w", pady=1)

                    ctk.CTkLabel(
                        details_frame,
                        text=f"Stock: {stock}",
                        font=("Arial", 11)
                    ).grid(row=2, column=0, sticky="w", pady=1)

                    ctk.CTkLabel(
                        details_frame,
                        text=f"Type: {self.selected_subcategory}",
                        font=("Arial", 11)
                    ).grid(row=3, column=0, sticky="w", pady=1)
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error loading product info: {e}")
            finally:
                conn.close()
        else:
            ctk.CTkLabel(
                self.selected_product_frame,
                text="Select a product from the menu",
                font=("Arial", 12)
            ).pack(pady=10)

    def load_addons(self):
        for widget in self.addons_container.winfo_children():
            widget.destroy()

        if not hasattr(self, 'selected_product'):
            return

        category = self.current_category
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT name, price, stock FROM addons WHERE category=? AND stock > 0",
                (category,)
            )
            addons = cursor.fetchall()
            if addons:
                self.addon_vars = {}
                for name, price, stock in addons:
                    var = ctk.BooleanVar()
                    self.addon_vars[name] = var
                    ctk.CTkCheckBox(
                        self.addons_container,
                        text=f"{name} (+₱{price})",
                        variable=var,
                        font=("Arial", 11)
                    ).pack(anchor="w", pady=2)
            else:
                ctk.CTkLabel(
                    self.addons_container,
                    text="No add-ons available for this category",
                    font=("Arial", 10)
                ).pack(pady=10)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading addons: {e}")
        finally:
            conn.close()

    def add_to_cart(self):
        if not hasattr(self, 'selected_product'):
            messagebox.showwarning("Selection Error", "Please select a product first")
            return

        selected_product = self.selected_product
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT price, stock FROM menu WHERE name = ?",
                (selected_product,)
            )
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Selected product not found")
                return

            base_price, stock = result
            if stock <= 0:
                messagebox.showerror("Out of Stock", f"Sorry, {selected_product} is out of stock!")
                return

            if self.size_var.get() == "Large":
                base_price += 15

            selected_addons = []
            addons_cost = 0
            if hasattr(self, 'addon_vars'):
                for addon_name, var in self.addon_vars.items():
                    if var.get():
                        cursor.execute(
                            "SELECT price, stock FROM addons WHERE name = ?",
                            (addon_name,)
                        )
                        addon_result = cursor.fetchone()
                        if addon_result:
                            addon_price, addon_stock = addon_result
                            if addon_stock <= 0:
                                messagebox.showwarning(
                                    "Out of Stock", f"Sorry, {addon_name} is out of stock!")
                                continue
                            selected_addons.append(addon_name)
                            addons_cost += addon_price

            total_price = base_price + addons_cost
            addons_text = ", ".join(selected_addons) if selected_addons else "None"

            temperature = (
                self.temp_var.get()
                if any(x in self.selected_subcategory for x in ["Coffee", "Tea", "Drinks"])
                else "N/A"
            )

            cart_item = {
                'product_name': selected_product,
                'size': self.size_var.get(),
                'temperature': temperature,
                'addons': selected_addons,
                'addons_text': addons_text,
                'price': total_price,
                'base_price': base_price,
                'addons_cost': addons_cost,
            }

            self.cart_items.append(cart_item)
            self.refresh_cart()

            if hasattr(self, 'addon_vars'):
                for var in self.addon_vars.values():
                    var.set(False)

            messagebox.showinfo("Success", f"{selected_product} added to cart!")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error adding to cart: {e}")
        finally:
            conn.close()

    def remove_from_cart(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an item to remove")
            return

        for item in selected:
            index = self.cart_tree.index(item)
            if 0 <= index < len(self.cart_items):
                self.cart_items.pop(index)

        self.refresh_cart()

    def clear_cart(self):
        if not self.cart_items:
            messagebox.showinfo("Info", "Cart is already empty")
            return

        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear the cart?"):
            self.cart_items = []
            self.refresh_cart()

    def refresh_cart(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        total_amount = 0
        for item in self.cart_items:
            self.cart_tree.insert(
                "", "end",
                values=(
                    item['product_name'],
                    item['size'],
                    item['temperature'],
                    item['addons_text'],
                    f"₱{item['price']}"
                )
            )
            total_amount += item['price']

        self.cart_total_label.configure(text=f"Total: ₱{total_amount:.2f}")

    def check_stock_availability(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            for item in self.cart_items:
                cursor.execute(
                    "SELECT stock FROM menu WHERE name = ?",
                    (item['product_name'],)
                )
                result = cursor.fetchone()
                if not result or result[0] <= 0:
                    messagebox.showerror(
                        "Out of Stock", f"Sorry, {item['product_name']} is out of stock!")
                    return False

                for addon in item['addons']:
                    cursor.execute(
                        "SELECT stock FROM addons WHERE name = ?",
                        (addon,)
                    )
                    addon_result = cursor.fetchone()
                    if not addon_result or addon_result[0] <= 0:
                        messagebox.showerror(
                            "Out of Stock", f"Sorry, {addon} is out of stock!")
                        return False
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error checking stock: {e}")
            return False
        finally:
            conn.close()

    def update_stock_after_order(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            for item in self.cart_items:
                cursor.execute(
                    "UPDATE menu SET stock = stock - 1 WHERE name = ?",
                    (item['product_name'],)
                )
                for addon in item['addons']:
                    cursor.execute(
                        "UPDATE addons SET stock = stock - 1 WHERE name = ?",
                        (addon,)
                    )
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error updating stock: {e}")
        finally:
            conn.close()

    def checkout(self):
        if not self.cart_items:
            messagebox.showwarning("Cart Empty", "Please add items to cart before checkout")
            return

        total = sum(item['price'] for item in self.cart_items)
        if not self.check_stock_availability():
            return

        order_details = {
            "customer": f"#{self.customer_number}",
            "items": self.cart_items.copy(),
            "service": self.service_type.get(),
            "packaging": self.packaging_type.get()
            if self.service_type.get() == "Take-out" else "None",
            "total": total,
            "status": "Waiting",
        }

        self.order_queue.append(order_details)
        self.update_stock_after_order()

        messagebox.showinfo(
            "Order Placed",
            f"Order #{self.customer_number} placed successfully!\n"
            f"Total: ₱{total:.2f}\n"
            f"Service: {self.service_type.get()}\n"
            f"Status: Waiting"
        )

        self.customer_number += 1
        self.cart_items = []
        self.refresh_cart()
        self.update_queue_display()
        self.select_category(self.current_category)

    # ===== Queue / orders =====

    def setup_queue_tab(self):
        # now done in queue_tab.py
        pass

    def prepare_next_order(self):
        if not self.order_queue:
            messagebox.showinfo("Info", "No orders in queue")
            return

        for order in self.order_queue:
            if order["status"] == "Waiting":
                order["status"] = "Preparing"
                messagebox.showinfo(
                    "Order Preparation",
                    f"Now preparing order {order['customer']}"
                )
                break

        self.update_queue_display()

    def serve_order(self):
        if not self.order_queue:
            messagebox.showinfo("Info", "No orders in queue")
            return

        for order in self.order_queue:
            if order["status"] == "Preparing":
                order["status"] = "Served"
                self.save_order_to_db(order)
                self.show_receipt(order)
                break

        self.order_queue = [o for o in self.order_queue if o["status"] != "Served"]
        self.update_queue_display()

    def save_order_to_db(self, order):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO orders (
                    customer_number, order_name, add_ons, size, temperature,
                    service_type, packaging_type, total, status, order_time
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order["customer"],
                ", ".join([item['product_name'] for item in order["items"]]),
                ", ".join([item['addons_text'] for item in order["items"]]),
                order["items"][0]['size'] if order["items"] else "Regular",
                order["items"][0]['temperature'] if order["items"] else "Hot",
                order["service"],
                order["packaging"],
                order["total"],
                order["status"],
                datetime.now()
            ))
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error saving order: {e}")
        finally:
            conn.close()

    def show_receipt(self, order):
        receipt_window = ctk.CTkToplevel(self.root)
        receipt_window.title(f"Receipt - {order['customer']}")
        receipt_window.geometry("400x600")
        receipt_window.transient(self.root)
        receipt_window.grab_set()

        receipt_content = ctk.CTkFrame(receipt_window)
        receipt_content.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            receipt_content, text="☕ BrewVerse Café ☕",
            font=("Courier New", 20, "bold")
        ).pack(pady=10)

        ctk.CTkLabel(
            receipt_content, text="RECEIPT",
            font=("Courier New", 16, "bold")
        ).pack(pady=5)

        details_frame = ctk.CTkFrame(receipt_content)
        details_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            details_frame, text=f"Order: {order['customer']}",
            font=("Courier New", 12, "bold")
        ).pack(anchor="w", pady=2)

        ctk.CTkLabel(
            details_frame, text=f"Service: {order['service']}",
            font=("Courier New", 11)
        ).pack(anchor="w", pady=1)

        if order['packaging'] != "None":
            ctk.CTkLabel(
                details_frame, text=f"Packaging: {order['packaging']}",
                font=("Courier New", 11)
            ).pack(anchor="w", pady=1)

        ctk.CTkLabel(
            details_frame,
            text=f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            font=("Courier New", 10)
        ).pack(anchor="w", pady=2)

        ctk.CTkFrame(
            receipt_content, height=2, fg_color="#333333"
        ).pack(fill="x", pady=10)

        items_frame = ctk.CTkFrame(receipt_content)
        items_frame.pack(fill="x", pady=5)

        for item in order["items"]:
            item_frame = ctk.CTkFrame(items_frame)
            item_frame.pack(fill="x", pady=2)

            main_item_text = f"{item['product_name']}"
            if item['size'] != "Regular":
                main_item_text += f" ({item['size']})"
            if item['temperature'] != "N/A":
                main_item_text += f" - {item['temperature']}"

            ctk.CTkLabel(
                item_frame, text=main_item_text,
                font=("Courier New", 11, "bold")
            ).pack(anchor="w")

            if item['addons_text'] != "None":
                for addon in item['addons_text'].split(", "):
                    ctk.CTkLabel(
                        item_frame, text=f"  + {addon}",
                        font=("Courier New", 10),
                        text_color="#666666"
                    ).pack(anchor="w")

            ctk.CTkLabel(
                item_frame, text=f"  ₱{item['price']}",
                font=("Courier New", 11)
            ).pack(anchor="e")

        ctk.CTkFrame(
            receipt_content, height=2, fg_color="#333333"
        ).pack(fill="x", pady=10)

        total_frame = ctk.CTkFrame(receipt_content)
        total_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            total_frame, text=f"TOTAL: ₱{order['total']:.2f}",
            font=("Courier New", 14, "bold")
        ).pack(anchor="e")

        thank_you_frame = ctk.CTkFrame(receipt_content)
        thank_you_frame.pack(fill="x", pady=20)

        ctk.CTkLabel(
            thank_you_frame, text="Thank you for your order!",
            font=("Courier New", 12, "bold")
        ).pack(pady=5)

        ctk.CTkLabel(
            thank_you_frame, text="Please visit again! ☕",
            font=("Courier New", 10)
        ).pack(pady=2)

        ctk.CTkButton(
            receipt_window, text="Close Receipt",
            command=receipt_window.destroy,
            fg_color="#8B4513"
        ).pack(pady=20)

    def update_queue_display(self):
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)

        for order in self.order_queue:
            items_text = ", ".join([i['product_name'] for i in order["items"]])
            self.queue_tree.insert(
                "", "end",
                values=(
                    order["customer"],
                    items_text,
                    order["service"],
                    order["packaging"],
                    order["status"],
                )
            )

    # ===== Image management =====

    def upload_product_image(self):
        image_path = self.image_manager.upload_image(self.root)
        if image_path:
            self.current_image_path = image_path
            self.image_path_label.configure(text=os.path.basename(image_path))
            self.show_image_preview(image_path)

    def clear_product_image(self):
        self.current_image_path = None
        self.image_path_label.configure(text="No image selected")
        self.clear_image_preview()

    def show_image_preview(self, image_path):
        try:
            photo = self.image_manager.get_image_preview(image_path, size=(100, 100))
            self.image_preview_label.configure(image=photo, text="")
            self.image_preview_label.image = photo
        except Exception as e:
            print(f"Error loading image preview: {e}")
            self.clear_image_preview()

    def clear_image_preview(self):
        self.image_preview_label.configure(image=None, text="No preview")
        if hasattr(self.image_preview_label, 'image'):
            self.image_preview_label.image = None

    # ===== Menu CRUD & inventory =====

    def load_menu(self):
        self.current_filter_category = "All"
        self.current_filter_subcategory = "All Subcategories"
        self.search_entry.delete(0, "end")
        self.apply_filters()

    def on_menu_selection(self, event):
        selected = self.menu_tree.selection()
        if not selected:
            return

        item = self.menu_tree.item(selected[0])
        values = item['values']

        if values:
            self.menu_name_entry.delete(0, "end")
            self.menu_name_entry.insert(0, values[1])

            self.menu_category_combobox.set(values[2])
            self.menu_subcategory_combobox.set(values[3])

            self.menu_price_entry.delete(0, "end")
            self.menu_price_entry.insert(0, str(values[4]).replace('₱', ''))

            self.menu_stock_entry.delete(0, "end")
            self.menu_stock_entry.insert(0, str(values[5]))

            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT image_path FROM menu WHERE id=?", (values[0],))
                result = cursor.fetchone()
                if result and result[0]:
                    self.current_image_path = result[0]
                    self.image_path_label.configure(text=os.path.basename(result[0]))
                    self.show_image_preview(result[0])
                else:
                    self.current_image_path = None
                    self.image_path_label.configure(text="No image")
                    self.clear_image_preview()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error loading image: {e}")
            finally:
                conn.close()

    def add_product(self):
        name = self.menu_name_entry.get().strip()
        category = self.menu_category_combobox.get().strip()
        subcategory = self.menu_subcategory_combobox.get().strip()
        price_text = self.menu_price_entry.get().strip()
        stock_text = self.menu_stock_entry.get().strip()

        if not all([name, category, subcategory, price_text, stock_text]):
            messagebox.showwarning("Input Error", "Please fill all fields")
            return

        try:
            price = float(price_text)
            stock = int(stock_text)
        except ValueError:
            messagebox.showerror("Error", "Price must be a number and stock must be an integer")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            image_path = self.current_image_path or os.path.join(IMAGES_DIR, "default.jpg")
            cursor.execute(
                "INSERT INTO menu (name, category, subcategory, price, stock, image_path) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (name, category, subcategory, price, stock, image_path)
            )
            conn.commit()
            self.load_menu()
            messagebox.showinfo("Success", f"Product '{name}' added successfully!")
            self.clear_form()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Product '{name}' already exists!")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error adding product: {e}")
        finally:
            conn.close()

    def update_product(self):
        selected = self.menu_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a product to update")
            return

        item = self.menu_tree.item(selected[0])
        item_id = item['values'][0]

        name = self.menu_name_entry.get().strip()
        category = self.menu_category_combobox.get().strip()
        subcategory = self.menu_subcategory_combobox.get().strip()
        price_text = self.menu_price_entry.get().strip()
        stock_text = self.menu_stock_entry.get().strip()

        if not any([name, category, subcategory, price_text, stock_text]) and not self.current_image_path:
            messagebox.showwarning("Input Error", "Please enter at least one field to update")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            updates = []
            params = []

            if name:
                updates.append("name = ?")
                params.append(name)
            if category:
                updates.append("category = ?")
                params.append(category)
            if subcategory:
                updates.append("subcategory = ?")
                params.append(subcategory)
            if price_text:
                try:
                    price = float(price_text)
                    updates.append("price = ?")
                    params.append(price)
                except ValueError:
                    messagebox.showerror("Error", "Price must be a number")
                    return
            if stock_text:
                try:
                    stock = int(stock_text)
                    updates.append("stock = ?")
                    params.append(stock)
                except ValueError:
                    messagebox.showerror("Error", "Stock must be an integer")
                    return

            if self.current_image_path:
                updates.append("image_path = ?")
                params.append(self.current_image_path)

            if not updates:
                messagebox.showwarning("Input Error", "No changes to update")
                return

            params.append(item_id)
            query = f"UPDATE menu SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()

            self.load_menu()
            messagebox.showinfo("Success", "Product updated successfully!")
            self.clear_form()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error updating product: {e}")
        finally:
            conn.close()

    def delete_product(self):
        selected = self.menu_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a product to delete")
            return

        item = self.menu_tree.item(selected[0])
        product_name = item['values'][1]

        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{product_name}'?"):
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT image_path FROM menu WHERE id=?", (item['values'][0],))
            result = cursor.fetchone()
            image_path = result[0] if result else None

            cursor.execute("DELETE FROM menu WHERE id = ?", (item['values'][0],))
            conn.commit()

            if image_path and os.path.exists(image_path) and not image_path.endswith("default.jpg"):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Warning: Could not delete image file: {e}")

            self.load_menu()
            messagebox.showinfo("Success", f"Product '{product_name}' deleted successfully!")
            self.clear_form()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error deleting product: {e}")
        finally:
            conn.close()

    def clear_form(self):
        self.menu_name_entry.delete(0, "end")
        self.menu_price_entry.delete(0, "end")
        self.menu_stock_entry.delete(0, "end")
        self.image_path_label.configure(text="No image selected")
        self.clear_image_preview()
        self.current_image_path = None

    def restock_product(self):
        selected = self.menu_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a product to restock")
            return

        stock_text = self.menu_stock_entry.get().strip()
        if not stock_text:
            messagebox.showwarning("Input Error", "Please enter stock quantity")
            return

        try:
            stock = int(stock_text)
        except ValueError:
            messagebox.showerror("Error", "Stock must be an integer")
            return

        item = self.menu_tree.item(selected[0])
        product_name = item['values'][1]

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE menu SET stock = ? WHERE id = ?", (stock, item['values'][0]))
            conn.commit()
            self.load_menu()
            messagebox.showinfo("Success", f"Product '{product_name}' restocked to {stock}")
            self.menu_stock_entry.delete(0, "end")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error restocking product: {e}")
        finally:
            conn.close()

    def on_takeout_selected(self):
        if not self.packaging_frame.winfo_ismapped():
            self.packaging_frame.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(
                self.packaging_frame,
                text="Packaging:",
                font=("Arial", 14, "bold")
            ).pack(side="left", padx=10)
            ctk.CTkRadioButton(
                self.packaging_frame,
                text="Standard",
                variable=self.packaging_type,
                value="Standard"
            ).pack(side="left", padx=5)
            ctk.CTkRadioButton(
                self.packaging_frame,
                text="Premium",
                variable=self.packaging_type,
                value="Premium"
            ).pack(side="left", padx=5)

    def show_sales_report(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT SUM(total) FROM orders WHERE status = 'Served'")
            total_sales = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Served'")
            order_count = cursor.fetchone()[0]

            cursor.execute("""
                SELECT order_name, COUNT(*) as count
                FROM orders
                WHERE status = 'Served'
                GROUP BY order_name
                ORDER BY count DESC
                LIMIT 5
            """)
            popular_items = cursor.fetchall()

            report_text = "📊 Sales Report\n\n"
            report_text += f"Total Orders: {order_count}\n"
            report_text += f"Total Revenue: ₱{total_sales:.2f}\n\n"
            report_text += "Most Popular Items:\n"
            for item, count in popular_items:
                report_text += f"• {item}: {count} orders\n"

            messagebox.showinfo("Sales Report", report_text)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error generating report: {e}")
        finally:
            conn.close()


    def show_sales_inventory(self):
        inventory_window = ctk.CTkToplevel(self.root)
        inventory_window.title("📦 Sales Inventory")
        inventory_window.geometry("1000x700")
        inventory_window.transient(self.root)
        inventory_window.grab_set()

        main_frame = ctk.CTkFrame(inventory_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(main_frame, text="📦 Sales Inventory",
                     font=("Arial", 20, "bold")).pack(pady=10)

        tabview = ctk.CTkTabview(main_frame)
        tabview.pack(fill="both", expand=True, pady=10)

        menu_tab = tabview.add("☕ Menu Items")
        self.setup_menu_inventory_tab(menu_tab)

        addons_tab = tabview.add("➕ Add-ons")
        self.setup_addons_inventory_tab(addons_tab)

        alerts_tab = tabview.add("⚠️ Low Stock Alerts")
        self.setup_low_stock_tab(alerts_tab)

        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=10)

        ctk.CTkButton(
            button_frame, text="🔄 Refresh Inventory",
            command=self.refresh_inventory_data,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame, text="📊 Export Report",
            command=self.export_inventory_report,
            width=150, fg_color="#8b522e8e"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame, text="📧 Email Alerts",
            command=self.email_low_stock_alerts,
            width=150, fg_color="#b45f06"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame, text="🗑️ Close",
            command=inventory_window.destroy,
            width=100
        ).pack(side="right", padx=5)


    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.root.destroy()
            start_app_with_login()


def start_app():
    root = ctk.CTk()
    CafeShopSystem(root)
    root.mainloop()


def start_app_with_login():
    LoginWindow(on_login_success=start_app)


if __name__ == "__main__":
    init_db()
    start_app_with_login()
