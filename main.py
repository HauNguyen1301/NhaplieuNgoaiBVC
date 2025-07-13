import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import sqlite3
from main_panel import MainPanel

class LoginPanel(ttk.Frame):
    """A frame that contains the login widgets."""
    def __init__(self, parent, on_login_success):
        super().__init__(parent, padding="20")
        self.on_login_success = on_login_success
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="Tên đăng nhập:").grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=0, column=1, sticky="ew")
        self.username_entry.focus()

        ttk.Label(self, text="Mật khẩu:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1, sticky="ew")

        login_button = ttk.Button(self, text="Đăng nhập", command=self.login, bootstyle=SUCCESS)
        login_button.grid(row=2, column=1, sticky="e", pady=10)

        # Bind Enter key to login
        self.winfo_toplevel().bind('<Return>', lambda event: self.login())

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên đăng nhập và mật khẩu.")
            return

        user = self.check_credentials(username, password)
        if user:
            self.on_login_success(user)
        else:
            messagebox.showerror("Đăng nhập thất bại", "Tên đăng nhập hoặc mật khẩu không đúng.")

    def check_credentials(self, username, password):
        conn = sqlite3.connect('boithuong.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE Username = ? AND PasswordHash = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        return user

class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="litera")
        self.title("Chương trình Nhập liệu Bồi thường")
        self.geometry("800x600")
        self.current_user = None
        self.show_login_screen()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_window()
        self.title("Đăng nhập")
        
        # A container to center the login panel
        center_frame = ttk.Frame(self)
        center_frame.pack(fill="both", expand=True)
        
        login_panel = LoginPanel(center_frame, self.handle_login_success)
        login_panel.place(relx=0.5, rely=0.5, anchor='center', width=300)

    def handle_login_success(self, user_info):
        self.current_user = user_info
        self.show_main_screen()

    def show_main_screen(self):
        self.clear_window()
        self.title("Chương trình Nhập liệu Bồi thường")
        main_panel = MainPanel(self, self.current_user, self.logout)
        main_panel.pack(fill="both", expand=True)

    def logout(self):
        if messagebox.askyesno("Xác nhận đăng xuất", "Bạn có chắc chắn muốn đăng xuất không?"):
            self.current_user = None
            self.show_login_screen()

if __name__ == "__main__":
    app = App()
    app.mainloop()
