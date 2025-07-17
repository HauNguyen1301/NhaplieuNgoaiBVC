import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry
from database import database_manager as db
from datetime import datetime

class QuanLySoLieuFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        # Frame chứa các bộ lọc
        filter_frame = ttk.Labelframe(self, text="Bộ lọc tìm kiếm", padding=10)
        filter_frame.pack(padx=10, pady=10, fill='x')

        # --- Dòng 1: Phòng ban và Cán bộ ---
        row1 = ttk.Frame(filter_frame)
        row1.pack(fill='x', pady=5)

        # Dropdown Phòng Ban
        ttk.Label(row1, text="Phòng ban:").pack(side='left', padx=(0, 5))
        self.phong_ban_combo = ttk.Combobox(row1, state="readonly", width=25)
        self.phong_ban_combo.pack(side='left', padx=5)
        self.phong_ban_combo.bind("<<ComboboxSelected>>", self.on_phong_ban_selected)

        # Dropdown Cán bộ
        ttk.Label(row1, text="Cán bộ:").pack(side='left', padx=(20, 5))
        self.can_bo_combo = ttk.Combobox(row1, state="readonly", width=25)
        self.can_bo_combo.pack(side='left', padx=5)

        # --- Dòng 2: Tình trạng --- 
        row2 = ttk.Frame(filter_frame)
        row2.pack(fill='x', pady=5)

        # Dropdown Tình trạng hồ sơ
        ttk.Label(row2, text="Tình trạng:").pack(side='left', padx=(0, 5))
        self.tinh_trang_combo = ttk.Combobox(row2, state="readonly", width=25)
        self.tinh_trang_combo.pack(side='left', padx=5)

        # --- Dòng 3: Ngày duyệt ---
        row3 = ttk.Frame(filter_frame)
        row3.pack(fill='x', pady=5)
        ttk.Label(row3, text="Ngày duyệt:").pack(side='left', padx=(0,5))
        ttk.Label(row3, text="Từ").pack(side='left', padx=(0, 5))
        self.ngay_duyet_from = DateEntry(row3, width=12, bootstyle='primary', dateformat="%Y/%m/%d")
        self.ngay_duyet_from.pack(side='left', padx=5)
        ttk.Label(row3, text="Đến").pack(side='left', padx=(10, 5))
        self.ngay_duyet_to = DateEntry(row3, width=12, bootstyle='primary', dateformat="%Y/%m/%d")
        self.ngay_duyet_to.pack(side='left', padx=5)

        # --- Dòng 4: Ngày nhận hồ sơ ---
        row4 = ttk.Frame(filter_frame)
        row4.pack(fill='x', pady=5)
        ttk.Label(row4, text="Ngày nhận HS:").pack(side='left', padx=(0,5))
        ttk.Label(row4, text="Từ").pack(side='left', padx=(0, 5))
        self.ngay_nhan_from = DateEntry(row4, width=12, bootstyle='primary', dateformat="%Y/%m/%d")
        self.ngay_nhan_from.pack(side='left', padx=5)
        ttk.Label(row4, text="Đến").pack(side='left', padx=(10, 5))
        self.ngay_nhan_to = DateEntry(row4, width=12, bootstyle='primary', dateformat="%Y/%m/%d")
        self.ngay_nhan_to.pack(side='left', padx=5)

        # --- Dòng 5: Nút Tìm kiếm và bộ đếm ---
        row5 = ttk.Frame(filter_frame)
        row5.pack(fill='x', pady=(10, 5))

        # Frame để căn giữa các thành phần
        center_frame = ttk.Frame(row5)
        center_frame.pack()

        self.record_count_label = ttk.Label(center_frame, text="Số hồ sơ: 0")
        self.record_count_label.pack(side='left', padx=(0, 10), pady=5)

        self.search_button = ttk.Button(center_frame, text="Tìm kiếm", command=self.search_data, bootstyle="primary")
        self.search_button.pack(side='left', pady=5)

        # --- Khung kết quả --- 
        results_frame = ttk.Labelframe(self, text="Kết quả tìm kiếm", padding=10)
        results_frame.pack(padx=10, pady=10, fill='both', expand=True)

        # Treeview để hiển thị dữ liệu
        columns = ("so_ho_so", "ten_ndbh", "ma_san_pham", "tien_ycbt", "tien_bt", "tinh_trang", "ngay_nhan", "ngay_duyet", "can_bo")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings")

        # Định nghĩa các cột
        headings = {
            "so_ho_so": "Số Hồ Sơ",
            "ten_ndbh": "Tên NĐBH",
            "ma_san_pham": "Mã SP",
            "tien_ycbt": "Tiền YCBT",
            "tien_bt": "Tiền Bồi Thường",
            "tinh_trang": "Tình Trạng",
            "ngay_nhan": "Ngày Nhận",
            "ngay_duyet": "Ngày Duyệt",
            "can_bo": "Cán bộ BT"
        }
        for col, text in headings.items():
            self.tree.heading(col, text=text)

        # Cấu hình độ rộng cột
        col_widths = {
            "so_ho_so": 100, "ten_ndbh": 180, "ma_san_pham": 80, "tien_ycbt": 100,
            "tien_bt": 110, "tinh_trang": 100, "ngay_nhan": 90, "ngay_duyet": 90, "can_bo": 120
        }
        for col, width in col_widths.items():
            self.tree.column(col, width=width, anchor='w')

        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Load initial data
        self.load_phong_ban()
        self.load_tinh_trang()
        self.ngay_duyet_from.entry.delete(0, 'end')
        self.ngay_duyet_to.entry.delete(0, 'end')
        self.ngay_nhan_from.entry.delete(0, 'end')
        self.ngay_nhan_to.entry.delete(0, 'end')

    def search_data(self):
        # Xóa dữ liệu cũ trên Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Thu thập các giá trị từ bộ lọc
        def format_date(date_widget):
            date_str = date_widget.entry.get()
            if not date_str:
                return None
            
            # Thử các định dạng có thể có
            for fmt in ('%Y/%m/%d', '%d/%m/%Y', '%Y-%m-%d'):
                try:
                    return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    continue
            
            # Nếu không thành công, thử lấy từ thuộc tính date
            try:
                return date_widget.date.strftime('%Y-%m-%d')
            except AttributeError:
                pass

            return None

        params = {
            'phong_ban': self.phong_ban_combo.get(),
            'can_bo': self.can_bo_combo.get(),
            'tinh_trang': self.tinh_trang_combo.get(),
            'ngay_duyet_from': format_date(self.ngay_duyet_from),
            'ngay_duyet_to': format_date(self.ngay_duyet_to),
            'ngay_nhan_from': format_date(self.ngay_nhan_from),
            'ngay_nhan_to': format_date(self.ngay_nhan_to)
        }

        # Gọi hàm tìm kiếm từ database_manager
        results = db.search_ho_so_nang_cao(params)

        # Cập nhật số lượng hồ sơ
        self.record_count_label.config(text=f"Số hồ sơ: {len(results)}")

        # Hiển thị kết quả lên Treeview
        if results:
            for row in results:
                # Chuyển đổi kiểu trả về của libsql_client thành tuple dữ liệu
                if hasattr(row, 'values'):
                    row_data = tuple(row.values)
                elif isinstance(row, (list, tuple)):
                    row_data = tuple(row)
                else:
                    # Fallback: parse chuỗi '(a, b, c)'
                    row_data = tuple([col.strip(" '()") for col in str(row).split(',')])
                self.tree.insert('', 'end', values=row_data)


    def load_phong_ban(self):
        phong_bans = db.get_phong_bans()
        # Lấy giá trị đầu tiên của mỗi tuple
        phong_ban_names = [pb[0] for pb in phong_bans if pb]
        self.phong_ban_combo['values'] = ['Tất cả'] + phong_ban_names
        self.phong_ban_combo.current(0)
        self.on_phong_ban_selected(None) # Tải cán bộ cho "Tất cả"

    def on_phong_ban_selected(self, event):
        selected_phong_ban = self.phong_ban_combo.get()
        if selected_phong_ban == 'Tất cả':
            # get_all_nhan_vien() trả về (NhanVienID, HoTen)
            can_bos = db.get_all_nhan_vien()
            can_bo_names = [cb[1] for cb in can_bos if cb] # Lấy HoTen
        else:
            # get_can_bos_by_phong_ban() trả về (HoTen,)
            can_bos = db.get_can_bos_by_phong_ban(selected_phong_ban)
            can_bo_names = [cb[0] for cb in can_bos if cb] # Lấy HoTen
        self.can_bo_combo['values'] = ['Tất cả'] + can_bo_names
        self.can_bo_combo.current(0)

    def load_tinh_trang(self):
        tinh_trangs = db.get_all_tinh_trang()
        # Lấy tên tình trạng (cột thứ 2)
        tinh_trang_names = [tt[1] for tt in tinh_trangs if tt]
        self.tinh_trang_combo['values'] = ['Tất cả'] + tinh_trang_names
        self.tinh_trang_combo.current(0)
