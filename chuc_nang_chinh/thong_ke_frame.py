import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap
import threading
from database import database_manager as db_manager


class ThongKeFrame(ttk.Frame):
    def __init__(self, parent, user_info):
        super().__init__(parent)
        self.user_info = user_info
        self.create_widgets()

    def create_widgets(self):
        content_frame = self

        # Frame chứa các nút
        button_frame = ttkbootstrap.Frame(content_frame)
        button_frame.pack(fill='x', padx=10, pady=5)

        self.refresh_button = ttkbootstrap.Button(button_frame, text="Làm mới", command=lambda: self.start_loading_in_thread(self.load_all_ho_so), bootstyle="info")
        self.refresh_button.pack(side='left', padx=5)

        self.unresolved_button = ttkbootstrap.Button(button_frame, text="Hồ sơ chưa giải quyết", command=lambda: self.start_loading_in_thread(self.load_unresolved_ho_so), bootstyle="warning")
        self.unresolved_button.pack(side='left', padx=5)

        self.resolved_button = ttkbootstrap.Button(button_frame, text="Hồ sơ đã giải quyết", command=lambda: self.start_loading_in_thread(self.load_resolved_ho_so), bootstyle="success")
        self.resolved_button.pack(side='left', padx=5)

        # Treeview để hiển thị dữ liệu
        self.tree_frame = ttkbootstrap.Frame(content_frame)
        self.tree_frame.pack(expand=True, fill='both', padx=10, pady=5)

        self.loading_label = ttk.Label(self.tree_frame, text="Đang tải dữ liệu...", bootstyle="info")
        self.loading_label.pack(pady=20)

        columns = ('id', 'so_ho_so', 'ndbh', 'san_pham', 'so_tien_yc', 'tinh_trang', 'ngay_nhan', 'can_bo_bt', 'nguoi_nhap')
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings')

        # Định nghĩa các cột
        self.tree.heading('so_ho_so', text='Số Hồ sơ')
        self.tree.heading('ndbh', text='Tên NĐBH')
        self.tree.heading('san_pham', text='Mã Sản Phẩm')
        self.tree.heading('so_tien_yc', text='Số tiền YC')
        self.tree.heading('tinh_trang', text='Tình Trạng')
        self.tree.heading('ngay_nhan', text='Ngày nhận')
        self.tree.heading('can_bo_bt', text='Cán bộ bồi thường')
        self.tree.heading('nguoi_nhap', text='Người nhập')

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

        self.tree['displaycolumns'] = ('so_ho_so', 'ndbh', 'san_pham', 'so_tien_yc', 'tinh_trang', 'ngay_nhan', 'can_bo_bt', 'nguoi_nhap')

        scrollbar = ttk.Scrollbar(self.tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        self.tree.bind('<Double-1>', self.on_tree_double_click)

    def clear_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def populate_treeview(self, data):
        self.clear_treeview()
        for row in data:
            so_tien_yc = f"{row[4]:,.0f}" if row[4] is not None else ""
            ho_so_id, so_ho_so, ndbh, san_pham, _, tinh_trang, ngay_nhan, can_bo_bt, nguoi_nhap = (v or "" for v in row)
            self.tree.insert('', 'end', values=(ho_so_id, so_ho_so, ndbh, san_pham, so_tien_yc, tinh_trang, ngay_nhan, can_bo_bt, nguoi_nhap))

    def start_loading_in_thread(self, target_func):
        self.loading_label.pack(pady=20)
        self.tree.pack_forget()
        thread = threading.Thread(target=target_func)
        thread.daemon = True
        thread.start()

    def on_data_loaded(self, data, error=None):
        self.loading_label.pack_forget()
        self.tree.pack(expand=True, fill='both')
        if error:
            messagebox.showerror("Lỗi tải dữ liệu", f"Không thể tải danh sách hồ sơ: {error}")
        else:
            self.populate_treeview(data)

    def load_all_ho_so(self):
        try:
            user_id, role = self.user_info[0], self.user_info[3]
            data = db_manager.get_all_ho_so_for_thong_ke(user_id=user_id, role=role)
            self.after(0, self.on_data_loaded, data)
        except Exception as e:
            self.after(0, self.on_data_loaded, None, e)

    def load_unresolved_ho_so(self):
        try:
            user_id, role = self.user_info[0], self.user_info[3]
            data = db_manager.get_unresolved_ho_so_for_thong_ke(user_id=user_id, role=role)
            self.after(0, self.on_data_loaded, data)
        except Exception as e:
            self.after(0, self.on_data_loaded, None, e)

    def load_resolved_ho_so(self):
        try:
            user_id, role = self.user_info[0], self.user_info[3]
            data = db_manager.get_resolved_ho_so_for_thong_ke(user_id=user_id, role=role)
            self.after(0, self.on_data_loaded, data)
        except Exception as e:
            self.after(0, self.on_data_loaded, None, e)

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
        popup.geometry("600x800")
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
            "Người duyệt:": data_dict.get("NguoiDuyet"),
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

        # --- Hàm sao chép dữ liệu ---
        def copy_details_to_clipboard():
            """Tạo chuỗi văn bản từ chi tiết hồ sơ và sao chép vào clipboard."""
            try:
                text_to_copy = ""
                for label, value in fields.items():
                    # Đảm bảo giá trị là chuỗi, xử lý None
                    value_str = str(value) if value is not None else "-"
                    # Sử dụng ký tự tab (\t) để phân tách, giúp dễ dàng chuyển thành 2 cột trong Word
                    text_to_copy += f"{label}\t{value_str}\n"
                
                # Xóa clipboard cũ và thêm nội dung mới
                self.clipboard_clear()
                self.clipboard_append(text_to_copy)
                
                # Thông báo thành công
                messagebox.showinfo("Thành công", "Đã sao chép chi tiết hồ sơ vào clipboard.", parent=popup)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể sao chép: {e}", parent=popup)

        # --- Frame chứa các nút ---
        button_container = ttk.Frame(popup)
        button_container.pack(pady=10, fill='x', anchor='s')

        # Căn giữa các nút trong container
        button_container.columnconfigure(0, weight=1)
        button_container.columnconfigure(1, weight=1)

        # Nút Sao chép
        copy_button = ttk.Button(button_container, text="Sao chép tất cả", command=copy_details_to_clipboard, bootstyle="info")
        copy_button.grid(row=0, column=0, sticky='e', padx=(0, 5))

        # Nút đóng
        close_button = ttk.Button(button_container, text="Đóng", command=popup.destroy, bootstyle="secondary")
        close_button.grid(row=0, column=1, sticky='w', padx=(5, 0))
