import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from change_password_window import ChangePasswordWindow
from user_management_window import UserManagementWindow

class MainPanel(ttk.Frame):
    def __init__(self, parent, user_info, logout_callback):
        super().__init__(parent, padding="10")
        self.user_info = user_info
        self.logout_callback = logout_callback
        self.create_widgets()

    def create_widgets(self):
        """Creates the widgets for the main panel."""
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', pady=5)

        ttk.Label(header_frame, text=f"Xin chào, {self.user_info[1]} (Role: {self.user_info[3]})").pack(side=LEFT, padx=10)
        
        logout_button = ttk.Button(header_frame, text="Đăng xuất", command=self.logout_callback, bootstyle=(DANGER, OUTLINE))
        logout_button.pack(side=RIGHT, padx=5)

        change_password_button = ttk.Button(header_frame, text="Đổi mật khẩu", command=self.open_change_password_window, bootstyle=INFO)
        change_password_button.pack(side=RIGHT, padx=5)

        # Admin-only buttons
        if self.user_info and self.user_info[3] == 'admin':
            user_mgmt_button = ttk.Button(header_frame, text="Quản lý User", command=self.open_user_management, bootstyle=SECONDARY)
            user_mgmt_button.pack(side=RIGHT, padx=5)

        # Placeholder for the rest of the application content
        content_frame = ttk.Frame(self, padding="10")
        content_frame.pack(fill="both", expand=True)
        ttk.Label(content_frame, text="Đây là giao diện chính của ứng dụng.", font=("Helvetica", 16)).pack(pady=20)

    def open_change_password_window(self):
        # The user_id is the first element in the user_info tuple
        user_id = self.user_info[0]
        ChangePasswordWindow(self.winfo_toplevel(), user_id)

    def open_user_management(self):
        UserManagementWindow(self.winfo_toplevel())
