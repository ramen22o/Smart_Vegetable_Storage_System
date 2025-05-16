import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedStyle
from auth.user_manager import check_credentials, add_user

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Smart Vegetable Storage")
        self.root.geometry("450x550")
        
        # Apply modern theme
        self.style = ThemedStyle(self.root)
        self.style.set_theme("arc")  # One of the most modern themes available
        
        # Custom styling
        self.style.configure("TFrame", background="#f5f6f7")
        self.style.configure("TLabel", 
                            background="#f5f6f7", 
                            font=("Segoe UI", 10),
                            foreground="#333333")
        self.style.configure("TEntry", 
                            fieldbackground="#ffffff",
                            foreground="#333333",
                            padding=8,
                            bordercolor="#dddddd",
                            lightcolor="#dddddd",
                            darkcolor="#dddddd")
        self.style.configure("TButton", 
                            font=("Segoe UI", 10, "bold"), 
                            padding=8,
                            relief="flat")
        self.style.map("TButton",
                     foreground=[('pressed', '#4a6fa5'), ('active', '#5a7fb5')],
                     background=[('pressed', '#4a6fa5'), ('active', '#5a7fb5')])
        
        # Accent button style
        self.style.configure("Accent.TButton", 
                           foreground="#4a6fa5",
                           background="#4a6fa5",
                           font=("Segoe UI", 10, "bold"),
                           padding=10)
        
        # Main container
        self.main_frame = ttk.Frame(self.root, padding=(40, 30))
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Header with logo placeholder
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(pady=(0, 30))
        
        # Logo placeholder (you can replace with actual image)
        self.logo_label = ttk.Label(
            self.header_frame,
            text="🥦",  # Using vegetable emoji as placeholder
            font=("Segoe UI", 32),
            foreground="#4a6fa5"
        )
        self.logo_label.pack()
        
        self.header_label = ttk.Label(
            self.header_frame, 
            text="SMART VEGETABLE STORAGE", 
            font=("Segoe UI", 14, "bold"),
            foreground="#4a6fa5"
        )
        self.header_label.pack(pady=(10, 0))
        
        # Form frame with card-like appearance
        self.form_frame = ttk.Frame(
            self.main_frame,
            padding=(30, 25),
            style="Card.TFrame"
        )
        self.form_frame.pack(fill=tk.X)
        
        # Custom style for card effect
        self.style.configure("Card.TFrame",
                            background="#ffffff",
                            relief="solid",
                            borderwidth=1,
                            bordercolor="#e1e5e9")
        
        # Username field
        self.username_label = ttk.Label(
            self.form_frame, 
            text="Username",
            font=("Segoe UI", 9, "bold"),
            foreground="#555555"
        )
        self.username_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.username_entry = ttk.Entry(
            self.form_frame,
            font=("Segoe UI", 10)
        )
        self.username_entry.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Password field
        self.password_label = ttk.Label(
            self.form_frame, 
            text="Password",
            font=("Segoe UI", 9, "bold"),
            foreground="#555555"
        )
        self.password_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.password_entry = ttk.Entry(
            self.form_frame,
            show="•",
            font=("Segoe UI", 10)
        )
        self.password_entry.pack(fill=tk.X, pady=(0, 20), ipady=5)
        
        # Button container
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Login button
        self.login_button = ttk.Button(
            self.button_frame, 
            text="LOGIN", 
            command=self.login,
            style="Accent.TButton"
        )
        self.login_button.pack(side=tk.RIGHT, ipadx=20)
        
        # Register button (secondary)
        self.register_button = ttk.Button(
            self.button_frame, 
            text="REGISTER", 
            command=self.register
        )
        self.register_button.pack(side=tk.RIGHT, ipadx=20, padx=(0, 10))
        
        # Footer
        self.footer_label = ttk.Label(
            self.main_frame,
            text="© 2023 Smart Vegetable Storage System",
            font=("Segoe UI", 8),
            foreground="#999999"
        )
        self.footer_label.pack(side=tk.BOTTOM, pady=(20, 0))
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.login())
        
        # Focus on username field by default
        self.username_entry.focus()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Required", "Please enter both username and password.")
            return

        if check_credentials(username, password):
            self.root.destroy()
            from storage_gui import StorageApp
            root = tk.Tk()
            app = StorageApp(root)
            root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        print(f"Username: '{username}'")  # Debug
        print(f"Password: '{password}'")  # Debug

        if not username or not password:
            messagebox.showwarning("Input Required", "Please enter both username and password.")
            return

        if add_user(username, password):
            messagebox.showinfo("Registration Successful", "User registered successfully.")
        else:
            messagebox.showerror("Registration Failed", "Username already exists.")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set Windows DPI awareness for better scaling
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    app = LoginApp(root)
    root.mainloop()