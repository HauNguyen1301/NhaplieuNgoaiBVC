import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .change_password_window import ChangePasswordWindow
from .user_management_window import UserManagementWindow

# Import the new frames for the notebook
from .nhap_gyctt_frame import NhapGycttFrame
from .to_trinh_boi_thuong_frame import ToTrinhBoiThuongFrame
from .thong_ke_frame import ThongKeFrame
from .quan_ly_so_lieu_frame import QuanLySoLieuFrame

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

        # user_info tuple structure from the new query:
        # (UserID, Username, PasswordHash, Role, NhanVienID, HoTen, HR_PhongBan)
        #  0       1         2             3     4           5      6
        ho_ten = self.user_info[5]
        phong_ban = self.user_info[6]
        welcome_message = f"Xin chào, {ho_ten}"
        if phong_ban:
            welcome_message += f" ({phong_ban})"
        ttk.Label(header_frame, text=welcome_message).pack(side=LEFT, padx=10)
        
        logout_button = ttk.Button(header_frame, text="Đăng xuất", command=self.logout_callback, bootstyle=(DANGER, OUTLINE))
        logout_button.pack(side=RIGHT, padx=5)

        change_password_button = ttk.Button(header_frame, text="Đổi mật khẩu", command=self.open_change_password_window, bootstyle=INFO)
        change_password_button.pack(side=RIGHT, padx=5)

        # Admin-only buttons
        if self.user_info and self.user_info[3] == 'admin':
            user_mgmt_button = ttk.Button(header_frame, text="Quản lý User", command=self.open_user_management, bootstyle=SECONDARY)
            user_mgmt_button.pack(side=RIGHT, padx=5)

        # Create a Separator
        ttk.Separator(self, orient=HORIZONTAL).pack(fill='x', pady=10, padx=10)

        # Create the Notebook widget
        notebook = ttk.Notebook(self, bootstyle="primary")
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create instances of the frames
        nhap_gyctt_tab = NhapGycttFrame(notebook)
        to_trinh_tab = ToTrinhBoiThuongFrame(notebook)
        thong_ke_tab = ThongKeFrame(notebook)
        quan_ly_tab = QuanLySoLieuFrame(notebook)

        # Add frames to the notebook
        notebook.add(nhap_gyctt_tab, text="Nhập GYCTT")
        notebook.add(to_trinh_tab, text="Tờ trình bồi thường")
        notebook.add(thong_ke_tab, text="Thống kê")
        notebook.add(quan_ly_tab, text="Quản lý số liệu")


    def open_change_password_window(self):
        # The user_id is the first element in the user_info tuple
        user_id = self.user_info[0]
        ChangePasswordWindow(self.winfo_toplevel(), user_id)

    def open_user_management(self):
        UserManagementWindow(self.winfo_toplevel())
