import tkinter as tk
from tkinter import ttk
import ttkbootstrap
from database import database_manager as db_manager

class ThongKeFrame(ttkbootstrap.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.load_all_ho_so() # Tải tất cả hồ sơ khi khởi tạo

    def create_widgets(self):
        # Frame chứa các nút
        button_frame = ttkbootstrap.Frame(self)
        button_frame.pack(fill='x', padx=10, pady=5)

        self.refresh_button = ttkbootstrap.Button(button_frame, text="Làm mới", command=self.load_all_ho_so, bootstyle="info")
        self.refresh_button.pack(side='left', padx=5)

        self.unresolved_button = ttkbootstrap.Button(button_frame, text="Hồ sơ chưa giải quyết", command=self.load_unresolved_ho_so, bootstyle="warning")
        self.unresolved_button.pack(side='left', padx=5)

        self.resolved_button = ttkbootstrap.Button(button_frame, text="Hồ sơ đã giải quyết", command=self.load_resolved_ho_so, bootstyle="success")
        self.resolved_button.pack(side='left', padx=5)

        # Treeview để hiển thị dữ liệu
        tree_frame = ttkbootstrap.Frame(self)
        tree_frame.pack(expand=True, fill='both', padx=10, pady=5)

        columns = ('so_ho_so', 'ndbh', 'san_pham', 'so_tien_yc', 'tinh_trang', 'ngay_nhan', 'can_bo_bt')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        # Định nghĩa các cột
        self.tree.heading('so_ho_so', text='Số Hồ sơ')
        self.tree.heading('ndbh', text='Tên NĐBH')
        self.tree.heading('san_pham', text='Sản Phẩm')
        self.tree.heading('so_tien_yc', text='Số tiền YC')
        self.tree.heading('tinh_trang', text='Tình Trạng')
        self.tree.heading('ngay_nhan', text='Ngày nhận')
        self.tree.heading('can_bo_bt', text='Cán bộ bồi thường')

        # Cấu hình độ rộng và căn giữa cột
        for col in columns:
            self.tree.column(col, anchor='center')
        
        self.tree.column('so_ho_so', width=120)
        self.tree.column('ndbh', width=200)
        self.tree.column('san_pham', width=150)
        self.tree.column('so_tien_yc', width=120)
        self.tree.column('tinh_trang', width=150)
        self.tree.column('ngay_nhan', width=100)
        self.tree.column('can_bo_bt', width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.tree.pack(expand=True, fill='both')

    def clear_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def populate_treeview(self, data):
        self.clear_treeview()
        for row in data:
            # Data tuple: (SoHoSo, NDBH, SanPham, SoTienYC, TinhTrang, NgayNhan, CanBoBT)
            # Indices:      0      1      2         3         4          5         6
            
            # Format số tiền
            so_tien_yc = f"{row[3]:,.0f}" if row[3] is not None else ""
            
            # Lấy các giá trị khác, xử lý giá trị None
            so_ho_so = row[0] if row[0] is not None else ""
            ndbh = row[1] if row[1] is not None else ""
            san_pham = row[2] if row[2] is not None else ""
            tinh_trang = row[4] if row[4] is not None else ""
            ngay_nhan = row[5] if row[5] is not None else ""
            can_bo_bt = row[6] if row[6] is not None else ""

            self.tree.insert('', 'end', values=(so_ho_so, ndbh, san_pham, so_tien_yc, tinh_trang, ngay_nhan, can_bo_bt))

    def load_all_ho_so(self):
        data = db_manager.get_ho_so_for_statistic()
        self.populate_treeview(data)

    def load_unresolved_ho_so(self):
        # Tình trạng ID: 1, 2, 3, 4, 6
        unresolved_ids = (1, 2, 3, 4, 6)
        data = db_manager.get_ho_so_for_statistic(status_ids=unresolved_ids)
        self.populate_treeview(data)

    def load_resolved_ho_so(self):
        # Tình trạng ID: 5
        resolved_ids = (5,)
        data = db_manager.get_ho_so_for_statistic(status_ids=resolved_ids)
        self.populate_treeview(data)
