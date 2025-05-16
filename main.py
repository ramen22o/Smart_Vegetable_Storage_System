import tkinter as tk
from auth.login_gui import LoginApp

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()