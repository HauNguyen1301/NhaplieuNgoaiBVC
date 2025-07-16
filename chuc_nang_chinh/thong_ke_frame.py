import tkinter as tk
from tkinter import ttk
import ttkbootstrap
from database import database_manager as db_manager

class ThongKeFrame(ttkbootstrap.Frame):
    def __init__(self, parent, user_info):
        super().__init__(parent)
        self.user_info = user_info
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

        columns = ('id', 'so_ho_so', 'ndbh', 'san_pham', 'so_tien_yc', 'tinh_trang', 'ngay_nhan', 'can_bo_bt', 'nguoi_nhap')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        # Định nghĩa các cột
        self.tree.heading('so_ho_so', text='Số Hồ sơ')
        self.tree.heading('ndbh', text='Tên NĐBH')
        self.tree.heading('san_pham', text='Sản Phẩm')
        self.tree.heading('so_tien_yc', text='Số tiền YC')
        self.tree.heading('tinh_trang', text='Tình Trạng')
        self.tree.heading('ngay_nhan', text='Ngày nhận')
        self.tree.heading('can_bo_bt', text='Cán bộ bồi thường')
        self.tree.heading('nguoi_nhap', text='Người nhập')

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
        self.tree.column('nguoi_nhap', width=150)

        # Ẩn cột ID
        self.tree['displaycolumns'] = ('so_ho_so', 'ndbh', 'san_pham', 'so_tien_yc', 'tinh_trang', 'ngay_nhan', 'can_bo_bt', 'nguoi_nhap')

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.tree.pack(expand=True, fill='both')

        # Bắt sự kiện double click
        self.tree.bind('<Double-1>', self.on_tree_double_click)

    def clear_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def populate_treeview(self, data):
        self.clear_treeview()
        for row in data:
            # Data tuple: (ID, SoHoSo, NDBH, SanPham, SoTienYC, TinhTrang, NgayNhan, CanBoBT, NguoiNhap)
            # Indices:      0    1       2      3        4          5          6         7          8
            
            # Format số tiền
            so_tien_yc = f"{row[4]:,.0f}" if row[4] is not None else ""
            
            # Lấy các giá trị khác, xử lý giá trị None
            ho_so_id = row[0]
            so_ho_so = row[1] or ""
            ndbh = row[2] or ""
            san_pham = row[3] or ""
            tinh_trang = row[5] or ""
            ngay_nhan = row[6] or ""
            can_bo_bt = row[7] or ""
            nguoi_nhap = row[8] or ""

            self.tree.insert('', 'end', values=(ho_so_id, so_ho_so, ndbh, san_pham, so_tien_yc, tinh_trang, ngay_nhan, can_bo_bt, nguoi_nhap))

    def load_all_ho_so(self):
        phong_ban = None
        user_id_for_cbbt = None
        role = self.user_info[3].lower() if self.user_info else ''

        if role == 'leader':
            phong_ban = self.user_info[6]
        elif role in ('cbbt', 'xacthuc'):
            user_id_for_cbbt = self.user_info[0]

        data = db_manager.get_ho_so_for_statistic(phong_ban=phong_ban, user_id_for_cbbt=user_id_for_cbbt)
        self.populate_treeview(data)

    def load_unresolved_ho_so(self):
        phong_ban = None
        user_id_for_cbbt = None
        role = self.user_info[3].lower() if self.user_info else ''

        if role == 'leader':
            phong_ban = self.user_info[6]
        elif role in ('cbbt', 'xacthuc'):
            user_id_for_cbbt = self.user_info[0]
        
        unresolved_ids = (1, 2, 3, 4, 6)
        data = db_manager.get_ho_so_for_statistic(status_ids=unresolved_ids, phong_ban=phong_ban, user_id_for_cbbt=user_id_for_cbbt)
        self.populate_treeview(data)

    def load_resolved_ho_so(self):
        phong_ban = None
        user_id_for_cbbt = None
        role = self.user_info[3].lower() if self.user_info else ''

        if role == 'leader':
            phong_ban = self.user_info[6]
        elif role in ('cbbt', 'xacthuc'):
            user_id_for_cbbt = self.user_info[0]

        resolved_ids = (5,)
        data = db_manager.get_ho_so_for_statistic(status_ids=resolved_ids, phong_ban=phong_ban, user_id_for_cbbt=user_id_for_cbbt)
        self.populate_treeview(data)

    def on_tree_double_click(self, event):
        """Xử lý sự kiện nhấp đúp chuột vào một dòng trong Treeview."""
        selected_item = self.tree.focus() # Lấy item đang được chọn
        if not selected_item:
            return

        # Lấy dictionary của item được chọn, bao gồm cả cột ẩn
        item_data = self.tree.item(selected_item)
        ho_so_id = item_data['values'][0] # ID nằm ở cột đầu tiên (ẩn)

        # Lấy chi tiết hồ sơ từ DB bằng ID
        ho_so_data = db_manager.get_ho_so_details_for_display(ho_so_id)

        if ho_so_data:
            self.show_details_popup(ho_so_data)
        else:
            messagebox.showerror("Lỗi", f"Không tìm thấy chi tiết cho hồ sơ ID: {ho_so_id}")

    def show_details_popup(self, data_dict):
        """Hiển thị cửa sổ popup với chi tiết hồ sơ."""
        if not data_dict:
            messagebox.showwarning("Không có dữ liệu", "Không thể tải chi tiết hồ sơ.")
            return

        popup = tk.Toplevel(self)
        popup.title("Chi tiết Hồ sơ")
        popup.geometry("600x550") # Tăng chiều cao để chứa hết thông tin
        popup.grab_set()  # Modal

        # --- Tạo giao diện có thể cuộn --- #
        main_frame = ttk.Frame(popup)
        main_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

        canvas = tk.Canvas(main_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        details_frame = ttk.Frame(canvas, padding=10)
        canvas.create_window((0, 0), window=details_frame, anchor="nw")
        # ------------------------------------ #

        # Các trường thông tin cần hiển thị
        fields = {
            "Số hồ sơ:": data_dict.get("SoHoSo"),
            "Người được bảo hiểm:": data_dict.get("NguoiDuocBaoHiem"),
            "Khách hàng:": data_dict.get("KhachHang"),
            "Số thẻ bảo hiểm:": data_dict.get("SoTheBaoHiem"),
            "Số hợp đồng:": data_dict.get("SoHopDongBaoHiem"),
            "Sản phẩm:": data_dict.get("TenSanPham"),
            "Công ty thành viên:": data_dict.get("TenCongTy"),
            "Hiệu lực từ:": data_dict.get("HLBH_tu"),
            "Hiệu lực đến:": data_dict.get("HLBH_den"),
            "Ngày nhận hồ sơ:": data_dict.get("NgayNhanHoSo"),
            "Ngày rủi ro:": data_dict.get("NgayRuiRo"),
            "Loại bệnh:": data_dict.get("TenLoaiBenh"),
            "Mô tả nguyên nhân:": data_dict.get("MoTaNguyenNhan"),
            "Hậu quả:": data_dict.get("HauQua"),
            "Giải quyết:": data_dict.get("GiaiQuyet"),
            "Số tiền yêu cầu:": f'{data_dict.get("SoTienYeuCau", 0):,.0f} VNĐ',
            "Số tiền bồi thường:": f'{data_dict.get("SoTienBoiThuong", 0):,.0f} VNĐ',
            "Ngày bồi thường:": data_dict.get("NgayBoiThuong"),
            "Tình trạng:": data_dict.get("TenTinhTrang"),
            "Cán bộ bồi thường:": data_dict.get("CanBoBoiThuong"),
            "Người nhập:": data_dict.get("NguoiNhap"),
            "Ngày tạo:": data_dict.get("time_create"),
            "Ngày cập nhật:": data_dict.get("time_update")
        }

        # Hiển thị các trường thông tin
        for i, (label_text, value_text) in enumerate(fields.items()):
            # Label (tiêu đề)
            label = ttk.Label(details_frame, text=label_text, font=("Helvetica", 10, "bold"))
            label.grid(row=i, column=0, sticky="nw", padx=5, pady=5)

            # Value (giá trị)
            value_label = ttk.Label(details_frame, text=value_text if value_text else "-", wraplength=400, justify=tk.LEFT)
            value_label.grid(row=i, column=1, sticky="nw", padx=5, pady=5)

        # Nút đóng
        close_button = ttk.Button(popup, text="Đóng", command=popup.destroy, bootstyle="secondary")
        close_button.pack(pady=10)
