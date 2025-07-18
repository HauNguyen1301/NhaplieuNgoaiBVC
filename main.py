import sys
import asyncio

# Fix for asyncio on Windows in a background thread
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, Toplevel
import requests
import webbrowser
import json
from database import database_manager as db_manager
from packaging.version import parse as parse_version
from dotenv import load_dotenv
from app_version import __version__ as CURRENT_VERSION
from chuc_nang_chinh.main_panel import MainPanel

# Tải biến môi trường từ file .env ngay từ đầu
load_dotenv()

UPDATE_URL = "https://raw.githubusercontent.com/HauNguyen1301/NhaplieuNgoaiBVC/main/updates/latest.json"
DOWNLOAD_URL = "https://1drv.ms/f/c/5f21643f394cb276/EuvWU7JTZh9KjZxseBBRzrwBIIVDEryylRAb1rwBEU7hGQ?e=SaEX78"

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
        sql = """
            SELECT u.UserID, u.Username, u.PasswordHash, u.Role, u.NhanVienID, nv.HoTen, nv.HR_PhongBan
            FROM User u
            JOIN NhanVien nv ON u.NhanVienID = nv.NhanVienID
            WHERE u.Username = ? AND u.PasswordHash = ?
        """
        try:
            user = db_manager.fetch_one(sql, (username, password))
            return user
        except Exception as e:
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối đến cơ sở dữ liệu: {e}")
            return None

class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="litera")
        self.title("Chương trình Nhập liệu Bồi thường Ngoài BVC" + CURRENT_VERSION)
        self.geometry("1200x800")
        try:
            # Set an empty icon to prevent the default icon error
            self.iconphoto(False, ttk.PhotoImage())
        except Exception:
            # Fallback for environments where icon setting might fail
            pass
        self.current_user = None
        self.login_panel = None # Add this to hold the login panel instance
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
        
        self.login_panel = LoginPanel(center_frame, self.handle_login_success)
        self.login_panel.place(relx=0.5, rely=0.5, anchor='center', width=300)

    def handle_login_success(self, user_info):
        self.current_user = user_info
        # Unbind the event from the top-level window to prevent re-triggering
        self.unbind('<Return>')
        self.login_panel = None # Clear the reference
        self.show_main_screen()
        self.check_for_updates()

    def show_main_screen(self):
        self.clear_window()
        self.title("Chương trình Nhập liệu Bồi thường Ngoài BVC - version: " + CURRENT_VERSION)
        main_panel = MainPanel(self, self.current_user, self.logout)
        main_panel.pack(fill="both", expand=True)

    def logout(self):
        if messagebox.askyesno("Xác nhận đăng xuất", "Bạn có chắc chắn muốn đăng xuất không?"):
            self.current_user = None
            self.show_login_screen()

    def check_for_updates(self):
        try:
            response = requests.get(UPDATE_URL, timeout=5)
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
            latest_version = data.get('version')

            if latest_version and parse_version(latest_version) > parse_version(CURRENT_VERSION):
                self.show_update_popup(latest_version)

        except requests.RequestException as e:
            # Hiển thị thông báo lỗi thân thiện với người dùng
            messagebox.showerror(
                "Lỗi kiểm tra cập nhật",
                f"Không thể kiểm tra phiên bản mới. Vui lòng kiểm tra lại kết nối mạng của bạn.\n\nChi tiết lỗi: {e}",
                parent=self
            )
        except Exception as e:
            # Bắt các lỗi không mong muốn khác
            messagebox.showerror(
                "Lỗi không xác định",
                f"Đã xảy ra một lỗi không mong muốn trong quá trình kiểm tra cập nhật:\n\n{e}",
                parent=self
            )

    def show_update_popup(self, new_version):
        popup = Toplevel(self)
        popup.title("Có phiên bản mới")
        popup.geometry("350x150")
        popup.resizable(False, False)
        popup.transient(self) # Keep popup on top of the main window

        label = ttk.Label(popup, text=f"Đã có phiên bản mới ({new_version})!\nBạn có muốn tải về không?", padding=20, justify='center')
        label.pack()

        def open_download_link():
            webbrowser.open(DOWNLOAD_URL)
            popup.destroy()

        download_button = ttk.Button(popup, text="Tải về ngay", command=open_download_link, bootstyle=SUCCESS)
        download_button.pack(pady=10)

        # Center the popup
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        popup.grab_set() # Modal

if __name__ == "__main__":
    app = App()
    app.mainloop()
