import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk

class LoginWindow:
    """Beautiful full-screen login window optimized for medium desktops"""

    def __init__(self, on_login_success):
        self.on_login_success = on_login_success

        # Set appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        
        self.root = ctk.CTk()
        self.root.title("☕ BrewVerse Café - Barista Portal")
        
        # Get screen dimensions for responsive design
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Set for medium desktop (adjust based on common medium desktop resolutions)
        # Common medium desktop: 1366x768, 1440x900, 1600x900
        if self.screen_width >= 1600:
            # Large medium desktop
            self.window_width = 1400
            self.window_height = 800
        elif self.screen_width >= 1366:
            # Standard medium desktop
            self.window_width = 1200
            self.window_height = 700
        else:
            # Smaller screen
            self.window_width = 1000
            self.window_height = 600
        
        # Set window to calculated size
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        
        # Make it windowed fullscreen (not true fullscreen for better aesthetics)
        self.root.state('zoomed')  # Maximized window
        
        # Center the window
        self.root.update_idletasks()
        x = (self.screen_width // 2) - (self.window_width // 2)
        y = (self.screen_height // 2) - (self.window_height // 2)
        self.root.geometry(f'+{x}+{y}')
        
        # Configure responsive grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create main container
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        
        # Configure main container grid (2 columns for left/right panels)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Calculate responsive dimensions
        panel_width = self.window_width // 2 - 100  # Half width minus padding
        panel_height = self.window_height - 100     # Full height minus padding
        
        # Left side - Branding/Image area (responsive)
        left_frame = ctk.CTkFrame(main_container, 
                                  corner_radius=25,
                                  fg_color="#6F4E37")
        left_frame.grid(row=0, column=0, padx=(0, 20), pady=10, sticky="nsew")
        
        # Right side - Login form area (responsive)
        right_frame = ctk.CTkFrame(main_container, 
                                   corner_radius=25,
                                   fg_color="#F8F5F0")
        right_frame.grid(row=0, column=1, pady=10, sticky="nsew")
        
        # Configure grid for both frames
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=1)
        
        # Calculate responsive font sizes based on screen size
        if self.window_width >= 1400:
            # Large fonts for big screens
            logo_font_size = 100
            title_font_size = 42
            subtitle_font_size = 18
            welcome_font_size = 28
            login_header_font = 32
            label_font_size = 14
            entry_font_size = 14
            button_font_size = 16
            entry_width = 400
        elif self.window_width >= 1200:
            # Medium fonts for standard medium desktops
            logo_font_size = 80
            title_font_size = 36
            subtitle_font_size = 16
            welcome_font_size = 24
            login_header_font = 28
            label_font_size = 13
            entry_font_size = 13
            button_font_size = 15
            entry_width = 350
        else:
            # Smaller fonts for compact screens
            logo_font_size = 60
            title_font_size = 28
            subtitle_font_size = 14
            welcome_font_size = 20
            login_header_font = 24
            label_font_size = 12
            entry_font_size = 12
            button_font_size = 14
            entry_width = 300
        
        # Left Frame Content - Café Branding
        left_content = ctk.CTkFrame(left_frame, fg_color="transparent")
        left_content.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        
        # Café Logo/Icon (responsive)
        ctk.CTkLabel(left_content, 
                     text="☕", 
                     font=("Segoe UI Emoji", logo_font_size),
                     text_color="#FFFFFF").pack(pady=(40, 20))
        
        ctk.CTkLabel(left_content, 
                     text="BrewVerse Café", 
                     font=("Arial Rounded MT Bold", title_font_size),
                     text_color="#FFFFFF").pack(pady=(0, 10))
        
        ctk.CTkLabel(left_content, 
                     text="Artisanal Coffee Experience", 
                     font=("Arial", subtitle_font_size, "italic"),
                     text_color="#E8D9C5").pack(pady=(0, 30))
        
        # Separator
        separator = ctk.CTkFrame(left_content, height=2, fg_color="#E8D9C5")
        separator.pack(fill="x", pady=20)
        
        # Welcome message
        ctk.CTkLabel(left_content, 
                     text="Barista Portal", 
                     font=("Arial Rounded MT Bold", welcome_font_size),
                     text_color="#FFFFFF").pack(pady=(20, 10))
        
        ctk.CTkLabel(left_content, 
                     text="Welcome back! Please login to\naccess the coffee management system.",
                     font=("Arial", label_font_size),
                     text_color="#E8D9C5",
                     justify="center").pack(pady=(0, 40))
        
        # Right Frame Content - Login Form
        form_container = ctk.CTkFrame(right_frame, fg_color="transparent")
        form_container.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        
        # Form Header (responsive)
        ctk.CTkLabel(form_container, 
                     text="🔐 Barista Login", 
                     font=("Arial Rounded MT Bold", login_header_font),
                     text_color="#6F4E37").pack(pady=(30, 10))
        
        ctk.CTkLabel(form_container, 
                     text="Enter your credentials to continue", 
                     font=("Arial", label_font_size),
                     text_color="#8A7B6F").pack(pady=(0, 40))
        
        # Username Field (responsive)
        ctk.CTkLabel(form_container, 
                     text="Username", 
                     font=("Arial", label_font_size, "bold"),
                     text_color="#6F4E37",
                     anchor="w").pack(fill="x", pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            form_container, 
            placeholder_text="Enter your username",
            width=entry_width,
            height=45,
            font=("Arial", entry_font_size),
            corner_radius=10,
            border_color="#D4C6B8",
            fg_color="#FFFFFF",
            text_color="#3E2C1C"
        )
        self.username_entry.pack(pady=(0, 20))
        
        # Password Field (responsive)
        ctk.CTkLabel(form_container, 
                     text="Password", 
                     font=("Arial", label_font_size, "bold"),
                     text_color="#6F4E37",
                     anchor="w").pack(fill="x", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            form_container, 
            placeholder_text="Enter your password",
            width=entry_width,
            height=45,
            font=("Arial", entry_font_size),
            corner_radius=10,
            border_color="#D4C6B8",
            fg_color="#FFFFFF",
            text_color="#3E2C1C",
            show="•"
        )
        self.password_entry.pack(pady=(0, 30))
        
        # Login Button (responsive)
        self.login_button = ctk.CTkButton(
            form_container, 
            text="Login to Dashboard",
            width=entry_width,
            height=50,
            font=("Arial Rounded MT Bold", button_font_size),
            corner_radius=10,
            fg_color="#6F4E37",
            hover_color="#5C3E2E",
            command=self.check_login
        )
        self.login_button.pack(pady=(0, 20))
        
        # Forgot Password (Placeholder)
        ctk.CTkLabel(form_container, 
                     text="Forgot password?",
                     font=("Arial", label_font_size - 1, "underline"),
                     text_color="#8A7B6F",
                     cursor="hand2").pack(pady=(0, 30))
        
        # Demo credentials hint
        demo_frame = ctk.CTkFrame(form_container, fg_color="#F0E6D6", corner_radius=8)
        demo_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(demo_frame,
                     text="💡 Password hint: barista / coffee123",
                     font=("Arial", label_font_size - 1),
                     text_color="#6F4E37"
                     ).pack(padx=10, pady=8)
        
        # Exit Button (responsive)
        exit_button = ctk.CTkButton(
            form_container, 
            text="Exit System",
            width=entry_width // 2,
            height=40,
            font=("Arial", button_font_size - 1),
            corner_radius=8,
            fg_color="transparent",
            hover_color="#F0E6D6",
            text_color="#6F4E37",
            border_color="#D4C6B8",
            border_width=2,
            command=self.root.quit
        )
        exit_button.pack(pady=(0, 20))
        
        # Footer Note
        ctk.CTkLabel(form_container, 
                     text="© 2024 BrewVerse Café. For authorized personnel only.",
                     font=("Arial", 10),
                     text_color="#B8A99A").pack(side="bottom", pady=10)
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.check_login())
        
        # Bind Escape key to exit
        self.root.bind('<Escape>', lambda event: self.root.quit())
        
        # Focus on username field
        self.username_entry.focus_set()
        
        # Make window slightly resizable with minimum size
        self.root.resizable(True, True)
        self.root.minsize(800, 500)
        
        self.root.mainloop()

    def check_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username == "barista" and password == "coffee123":
            # Visual feedback before closing
            self.login_button.configure(
                text="✓ Login Successful!",
                fg_color="#4CAF50",
                hover_color="#45A049"
            )
            self.root.after(800, self.finalize_login)
        else:
            # Shake animation for invalid login
            self.shake_window()
            messagebox.showerror("Access Denied", 
                               "Invalid credentials. Please try again.")
            self.password_entry.delete(0, 'end')

    def shake_window(self):
        """Add a shake animation for invalid login"""
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        for _ in range(2):
            for dx in [15, -15, 15, -15, 0]:
                self.root.geometry(f"+{x+dx}+{y}")
                self.root.update()
                self.root.after(25)

    def finalize_login(self):
        """Finalize the login process"""
        messagebox.showinfo("Welcome", "👋 Welcome back, Barista!\n\nReady to brew some magic?")
        self.root.destroy()
        self.on_login_success()