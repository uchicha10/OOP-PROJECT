import os
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk


class ImageManager:
    """Manage product images - upload, resize, delete"""

    def __init__(self, images_dir="product_images"):
        self.images_dir = images_dir
        self.supported_formats = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
        self.ensure_images_directory()

    def ensure_images_directory(self):
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)

    def is_valid_image(self, file_path):
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except (IOError, SyntaxError):
            return False

    def get_unique_filename(self, original_filename):
        base_name = os.path.basename(original_filename)
        name, ext = os.path.splitext(base_name)
        counter = 1
        new_filename = base_name
        while os.path.exists(os.path.join(self.images_dir, new_filename)):
            new_filename = f"{name}_{counter}{ext}"
            counter += 1
        return new_filename

    def resize_image(self, image_path, max_size=(300, 300)):
        try:
            with Image.open(image_path) as img:
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                return img
        except Exception as e:
            raise Exception(f"Error resizing image: {str(e)}")

    def upload_image(self, parent_window):
        file_path = filedialog.askopenfilename(
            parent=parent_window,
            title="Select Product Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("All files", ".")
            ]
        )

        if not file_path:
            return None

        if not self.is_valid_image(file_path):
            messagebox.showerror("Invalid Image", "The selected file is not a valid image.")
            return None

        try:
            resized_img = self.resize_image(file_path)
            original_filename = os.path.basename(file_path)
            new_filename = self.get_unique_filename(original_filename)
            new_filepath = os.path.join(self.images_dir, new_filename)

            resized_img.save(new_filepath, 'JPEG', quality=85)
            messagebox.showinfo("Success", f"Image uploaded successfully as {new_filename}")
            return new_filepath
        except Exception as e:
            messagebox.showerror("Upload Error", f"Failed to upload image: {str(e)}")
            return None

    def delete_image(self, image_path):
        try:
            if image_path and os.path.exists(image_path) and not image_path.endswith("default.jpg"):
                os.remove(image_path)
                return True
        except Exception as e:
            print(f"Error deleting image: {e}")
        return False

    def get_image_preview(self, image_path, size=(100, 100)):
        try:
            if not image_path or not os.path.exists(image_path):
                default_path = os.path.join(self.images_dir, "default.jpg")
                if os.path.exists(default_path):
                    img = Image.open(default_path)
                else:
                    img = Image.new('RGB', size, color='#6f4e37')
            else:
                img = Image.open(image_path)

            img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image preview: {e}")
            img = Image.new('RGB', size, color='#6f4e37')
            return ImageTk.PhotoImage(img)
