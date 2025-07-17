import ttkbootstrap as ttk


class QuanLySoLieuFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        content_frame = self
        ttk.Label(content_frame, text="Đây là trang Quản lý số liệu", font=("Helvetica", 16)).pack(pady=20)
        # Các thành phần giao diện cho Quản lý số liệu sẽ được thêm vào đây
