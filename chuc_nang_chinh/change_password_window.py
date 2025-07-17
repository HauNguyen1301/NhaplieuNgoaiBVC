import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from database import database_manager as db_manager

class ChangePasswordWindow(ttk.Toplevel):
    def __init__(self, parent, user_id):
        super().__init__(parent, "Đổi mật khẩu")
        self.user_id = user_id
        self.geometry("400x200")
        self.transient(parent) # Keep this window on top of the parent
        self.grab_set() # Modal behavior

        try:
            self.iconphoto(False, ttk.PhotoImage())
        except Exception:
            pass

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_columnconfigure(1, weight=1)

        # Old Password
        ttk.Label(main_frame, text="Mật khẩu cũ:").grid(row=0, column=0, sticky="w", pady=5)
        self.old_password_entry = ttk.Entry(main_frame, show="*")
        self.old_password_entry.grid(row=0, column=1, sticky="ew")
        self.old_password_entry.focus()

        # New Password
        ttk.Label(main_frame, text="Mật khẩu mới:").grid(row=1, column=0, sticky="w", pady=5)
        self.new_password_entry = ttk.Entry(main_frame, show="*")
        self.new_password_entry.grid(row=1, column=1, sticky="ew")

        # Confirm New Password
        ttk.Label(main_frame, text="Xác nhận mật khẩu:").grid(row=2, column=0, sticky="w", pady=5)
        self.confirm_password_entry = ttk.Entry(main_frame, show="*")
        self.confirm_password_entry.grid(row=2, column=1, sticky="ew")

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=1, sticky="e", pady=15)

        save_button = ttk.Button(button_frame, text="Lưu thay đổi", command=self.change_password, bootstyle=SUCCESS)
        save_button.pack(side=LEFT, padx=5)

        cancel_button = ttk.Button(button_frame, text="Hủy", command=self.destroy, bootstyle=SECONDARY)
        cancel_button.pack(side=LEFT)

    def change_password(self):
        old_password = self.old_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not all([old_password, new_password, confirm_password]):
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin.", parent=self)
            return

        if new_password != confirm_password:
            messagebox.showerror("Lỗi", "Mật khẩu mới không khớp.", parent=self)
            return

        # Verify old password using the database manager
        user_record = db_manager.fetch_one("SELECT PasswordHash FROM User WHERE UserID = ?", (self.user_id,))

        if not user_record or user_record[0] != old_password:
            messagebox.showerror("Lỗi", "Mật khẩu cũ không đúng.", parent=self)
            return

        # Update to new password using the database manager
        success = db_manager.execute_query(
            "UPDATE User SET PasswordHash = ? WHERE UserID = ?",
            (new_password, self.user_id)
        )

        if success:
            messagebox.showinfo("Thành công", "Đổi mật khẩu thành công.", parent=self)
            self.destroy()
        else:
            messagebox.showerror("Lỗi cơ sở dữ liệu", "Không thể cập nhật mật khẩu.", parent=self)
