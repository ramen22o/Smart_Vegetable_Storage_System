import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk, ThemedStyle
from models.storage_system import StorageSystem
from models.vegetable import Vegetable


class StorageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Vegetable Storage System")
        self.root.geometry("1000x700")
        # Modern theme configuration
        self.style = ThemedStyle(self.root)
        self.style.set_theme("equilux")
        # Custom styling
        self.style.configure("TFrame", background=self.style.lookup("TFrame", "background"))
        self.style.configure("TLabel",
                             font=("Segoe UI", 10),
                             foreground="#ffffff",
                             background=self.style.lookup("TFrame", "background"))
        self.style.configure("TButton",
                             font=("Segoe UI", 10, "bold"),
                             padding=8,
                             relief="flat")
        self.style.map("TButton",
                       foreground=[('pressed', '#ffffff'), ('active', '#ffffff')],
                       background=[('pressed', '#3a7ebf'), ('active', '#4a8ecf')])
        # Custom notebook style
        self.style.configure("TNotebook", borderwidth=0)
        self.style.configure("TNotebook.Tab",
                             font=("Segoe UI", 10, "bold"),
                             padding=[15, 5],
                             foreground="#ffffff",
                             background="#2d2d2d",
                             lightcolor="#2d2d2d",
                             bordercolor="#2d2d2d")
        self.style.map("TNotebook.Tab",
                       background=[("selected", "#3a7ebf")],
                       foreground=[("selected", "#ffffff")])
        # Combobox styling
        self.style.configure("TCombobox",
                             fieldbackground="#ffffff",
                             foreground="#333333",
                             selectbackground="#3a7ebf",
                             selectforeground="#ffffff")
        # Accent button style
        self.style.configure("Accent.TButton",
                             foreground="#ffffff",
                             background="#3a7ebf",
                             font=("Segoe UI", 10, "bold"),
                             padding=10)
        self.storage_system = StorageSystem()
        self.create_widgets()
        self.update_bin_dropdowns()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=(20, 10))
        main_frame.pack(expand=True, fill=tk.BOTH)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header = ttk.Label(header_frame, text="Smart Vegetable Storage System", font=("Segoe UI", 20, "bold"), foreground="#3a7ebf")
        header.pack()
        subheader = ttk.Label(header_frame, text="Manage your vegetable storage with precision", font=("Segoe UI", 10), foreground="#aaaaaa")
        subheader.pack()

        tab_control = ttk.Notebook(main_frame)
        tab_control.pack(expand=True, fill=tk.BOTH)

        view_tab = ttk.Frame(tab_control, padding=20)
        tab_control.add(view_tab, text="👀 View Bins")
        search_frame = ttk.Frame(view_tab)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(search_frame, text="Bin ID:").pack(side=tk.LEFT, padx=(0, 10))
        self.bin_dropdown_view = ttk.Combobox(search_frame, state="readonly", font=("Segoe UI", 10))
        self.bin_dropdown_view.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=4)
        ttk.Button(search_frame, text="SHOW CONTENTS", command=self.show_bin_contents, style="Accent.TButton").pack(side=tk.RIGHT, padx=(10, 0))

        list_container = ttk.Frame(view_tab)
        list_container.pack(expand=True, fill=tk.BOTH)
        self.bin_listbox = tk.Listbox(list_container, width=50, height=15, font=("Segoe UI", 10), bg="#2d2d2d", fg="#ffffff", selectbackground="#3a7ebf", selectforeground="#ffffff")
        self.bin_listbox.pack(expand=True, fill=tk.BOTH, pady=(10, 0))
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.bin_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.bin_listbox.config(yscrollcommand=scrollbar.set)

        create_tab = ttk.Frame(tab_control, padding=20)
        tab_control.add(create_tab, text="🆕 Create Bin")
        create_form_frame = ttk.Frame(create_tab)
        create_form_frame.pack(expand=True, fill=tk.BOTH)
        create_fields = [("Bin ID:", "create_bin_id"), ("Max Capacity:", "create_max_cap"), ("Temperature (°C):", "create_temp"), ("Humidity (%):", "create_humid")]
        for label_text, attr_name in create_fields:
            self.create_modern_form_field(create_form_frame, label_text, attr_name)
        create_btn_frame = ttk.Frame(create_tab)
        create_btn_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(create_btn_frame, text="CREATE BIN", command=self.create_bin, style="Accent.TButton").pack(pady=10, ipadx=20)

        add_tab = ttk.Frame(tab_control, padding=20)
        tab_control.add(add_tab, text="➕ Add Vegetable")
        form_frame = ttk.Frame(add_tab)
        form_frame.pack(expand=True, fill=tk.BOTH)
        fields = [("Name:", "add_name"), ("Quantity:", "add_quantity"), ("Temperature (°C):", "add_temp"), ("Humidity (%):", "add_humid"), ("Expiry Date:", "add_expiry")]
        for label_text, attr_name in fields:
            self.create_modern_form_field(form_frame, label_text, attr_name)
        bin_frame = ttk.Frame(form_frame)
        bin_frame.pack(fill=tk.X, pady=8)
        ttk.Label(bin_frame, text="Bin ID:").pack(side=tk.LEFT, padx=(0, 10))
        self.bin_dropdown_add = ttk.Combobox(bin_frame, state="readonly", font=("Segoe UI", 10))
        self.bin_dropdown_add.pack(side=tk.RIGHT, expand=True, fill=tk.X, ipady=4)
        btn_frame = ttk.Frame(add_tab)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(btn_frame, text="ADD VEGETABLE", command=self.add_vegetable, style="Accent.TButton").pack(pady=10, ipadx=20)

        remove_tab = ttk.Frame(tab_control, padding=20)
        tab_control.add(remove_tab, text="➖ Remove Quantity")
        remove_form_frame = ttk.Frame(remove_tab)
        remove_form_frame.pack(expand=True, fill=tk.BOTH)
        bin_remove_frame = ttk.Frame(remove_form_frame)
        bin_remove_frame.pack(fill=tk.X, pady=8)
        ttk.Label(bin_remove_frame, text="Bin ID:").pack(side=tk.LEFT, padx=(0, 10))
        self.bin_dropdown_remove = ttk.Combobox(bin_remove_frame, state="readonly", font=("Segoe UI", 10))
        self.bin_dropdown_remove.pack(side=tk.RIGHT, expand=True, fill=tk.X, ipady=4)
        veg_remove_frame = ttk.Frame(remove_form_frame)
        veg_remove_frame.pack(fill=tk.X, pady=8)
        ttk.Label(veg_remove_frame, text="Vegetable Name:").pack(side=tk.LEFT, padx=(0, 10))
        self.remove_name = ttk.Entry(veg_remove_frame, font=("Segoe UI", 10))
        self.remove_name.pack(side=tk.RIGHT, expand=True, fill=tk.X, ipady=4)
        qty_remove_frame = ttk.Frame(remove_form_frame)
        qty_remove_frame.pack(fill=tk.X, pady=8)
        ttk.Label(qty_remove_frame, text="Quantity to Take:").pack(side=tk.LEFT, padx=(0, 10))
        self.remove_quantity = ttk.Entry(qty_remove_frame, font=("Segoe UI", 10))
        self.remove_quantity.pack(side=tk.RIGHT, expand=True, fill=tk.X, ipady=4)
        remove_btn_frame = ttk.Frame(remove_tab)
        remove_btn_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(remove_btn_frame, text="REMOVE QUANTITY", command=self.remove_vegetable_quantity, style="Accent.TButton").pack(pady=10, ipadx=20)

    def create_modern_form_field(self, parent, label_text, entry_name, var=None):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=8)
        ttk.Label(frame, text=label_text).pack(side=tk.LEFT, padx=(0, 10))
        entry = ttk.Entry(frame, font=("Segoe UI", 10))
        entry.pack(side=tk.RIGHT, expand=True, fill=tk.X, ipady=4)
        setattr(self, entry_name, entry)

    def update_bin_dropdowns(self):
        bin_ids = list(self.storage_system.bins.keys())
        self.bin_dropdown_add['values'] = bin_ids
        self.bin_dropdown_view['values'] = bin_ids
        self.bin_dropdown_remove['values'] = bin_ids
        if bin_ids:
            self.bin_dropdown_add.current(0)
            self.bin_dropdown_view.current(0)
            self.bin_dropdown_remove.current(0)

    def add_vegetable(self):
        try:
            name = self.add_name.get()
            quantity = int(self.add_quantity.get())
            temp = float(self.add_temp.get())
            humid = float(self.add_humid.get())
            expiry = self.add_expiry.get()
            bin_id = self.bin_dropdown_add.get()
            if not all([name, quantity, temp, humid, expiry, bin_id]):
                messagebox.showwarning("Input Error", "All fields are required.")
                return
            vegetable = Vegetable(name, quantity, temp, humid, expiry)
            if bin_id in self.storage_system.bins:
                if self.storage_system.add_vegetable_to_bin(bin_id, vegetable):
                    messagebox.showinfo("Success", f"Vegetable added to bin '{bin_id}'.")
                    self.add_name.delete(0, tk.END)
                    self.add_quantity.delete(0, tk.END)
                    self.add_temp.delete(0, tk.END)
                    self.add_humid.delete(0, tk.END)
                    self.add_expiry.delete(0, tk.END)
                else:
                    messagebox.showerror("Error", f"Failed to add vegetable to bin '{bin_id}'.")
            else:
                messagebox.showerror("Error", f"Bin '{bin_id}' does not exist.")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")

    def create_bin(self):
        try:
            bin_id = self.create_bin_id.get()
            max_cap = int(self.create_max_cap.get())
            temp = float(self.create_temp.get())
            humid = float(self.create_humid.get())
            if self.storage_system.create_bin(bin_id, max_cap, temp, humid):
                messagebox.showinfo("Success", "Bin created successfully.")
                self.update_bin_dropdowns()
                self.create_bin_id.delete(0, tk.END)
                self.create_max_cap.delete(0, tk.END)
                self.create_temp.delete(0, tk.END)
                self.create_humid.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Failed to create bin.")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")

    def show_bin_contents(self):
        bin_id = self.bin_dropdown_view.get()
        if not bin_id:
            messagebox.showwarning("Selection Required", "Please select a bin first.")
            return
        contents = self.storage_system.get_bin_contents(bin_id)
        self.bin_listbox.delete(0, tk.END)
        if not contents:
            self.bin_listbox.insert(tk.END, "No vegetables in this bin.")
        else:
            for veg in contents:
                self.bin_listbox.insert(tk.END, f"🏺 {str(veg)}")
        # Trigger FIFO warnings
        self.storage_system._check_fifo_warnings(bin_id, show_warning=True)

    def remove_vegetable_quantity(self):
        try:
            bin_id = self.bin_dropdown_remove.get()
            vegetable_name = self.remove_name.get()
            quantity_to_take = int(self.remove_quantity.get())
            if not bin_id or not vegetable_name or not quantity_to_take:
                messagebox.showwarning("Input Error", "All fields are required.")
                return
            taken = self.storage_system.take_out_vegetable_quantity(bin_id, vegetable_name, quantity_to_take)
            if taken > 0:
                messagebox.showinfo("Success", f"Removed {taken} units of '{vegetable_name}' from bin '{bin_id}'.")
                self.show_bin_contents()  # Refresh view tab contents
                self.remove_name.delete(0, tk.END)
                self.remove_quantity.delete(0, tk.END)
            else:
                messagebox.showerror("Error", f"Failed to remove '{vegetable_name}' from bin '{bin_id}'.")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid quantity.")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    root = ThemedTk(theme="equilux")
    root.configure(bg="#2d2d2d")
    app = StorageApp(root)
    root.mainloop()