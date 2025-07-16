import tkinter as tk
from tkinter import ttk, Text, TclError
from datetime import datetime
import ttkbootstrap
from ttkbootstrap.constants import SUCCESS
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.scrolled import ScrolledFrame

from ttkbootstrap.dialogs import Messagebox
from database import database_manager as db_manager

class EditGYCTTFrame(ttkbootstrap.Frame):
    def __init__(self, parent, hs_id, on_save_callback=None):
        super().__init__(parent)
        self.hs_id = hs_id
        self.on_save_callback = on_save_callback
        self.create_widgets()
        self.load_initial_data()
        self.load_data()

    def create_widgets(self):
        # --- Main Layout ---
        # Frame for buttons, placed at the bottom
        button_frame = ttk.Frame(self)
        button_frame.pack(side='bottom', fill='x', padx=10, pady=10)

        # ScrolledFrame for the main content, placed above the buttons
        scroll_frame = ScrolledFrame(self, autohide=True)
        scroll_frame.pack(side='top', fill='both', expand=True, padx=10, pady=(10, 0))

        # Use a PanedWindow to ensure two frames have equal width
        paned_window = ttk.PanedWindow(scroll_frame, orient='horizontal')
        paned_window.pack(fill='both', expand=True)

        # Main frames for content, placed inside the PanedWindow
        left_frame = ttk.LabelFrame(paned_window, text="Thông tin hồ sơ", padding=15)
        paned_window.add(left_frame, weight=1) # weight=1 ensures equal distribution
        
        right_frame = ttk.LabelFrame(paned_window, text="Sự kiện bảo hiểm", padding=15)
        paned_window.add(right_frame, weight=1) # weight=1 ensures equal distribution
        left_frame.grid_columnconfigure(1, weight=1)
        right_frame.grid_columnconfigure(1, weight=1)
        right_frame.rowconfigure(8, weight=1) # Configure row with Text widget to expand

        # --- Left Frame Widgets ---
        ttk.Label(left_frame, text="Ban cấp đơn:").grid(row=0, column=0, sticky="w", pady=5)
        self.ban_combo = ttk.Combobox(left_frame, state="readonly")
        self.ban_combo.grid(row=0, column=1, sticky="ew", pady=5)
        self.ban_combo.bind('<<ComboboxSelected>>', self.update_san_pham_dropdown)

        ttk.Label(left_frame, text="Sản phẩm:").grid(row=1, column=0, sticky="w", pady=5)
        self.san_pham_combo = ttk.Combobox(left_frame, state="readonly")
        self.san_pham_combo.grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(left_frame, text="Công ty thành viên:").grid(row=2, column=0, sticky="w", pady=5)
        self.cttv_combo = ttk.Combobox(left_frame, state="readonly")
        self.cttv_combo.grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(left_frame, text="Số thẻ bảo hiểm:").grid(row=3, column=0, sticky="w", pady=5)
        self.so_the_entry = ttk.Entry(left_frame)
        self.so_the_entry.grid(row=3, column=1, sticky="ew", pady=5)

        ttk.Label(left_frame, text="Số hợp đồng bảo hiểm:").grid(row=4, column=0, sticky="w", pady=5)
        self.so_hd_entry = ttk.Entry(left_frame)
        self.so_hd_entry.grid(row=4, column=1, sticky="ew", pady=5)

        ttk.Label(left_frame, text="Số GYCTT:").grid(row=5, column=0, sticky="w", pady=5)
        self.so_gyctt_entry = ttk.Entry(left_frame, state="readonly")
        self.so_gyctt_entry.grid(row=5, column=1, sticky="ew", pady=5)

        ttk.Label(left_frame, text="Người được bảo hiểm:").grid(row=6, column=0, sticky="w", pady=5)
        self.ndbh_entry = ttk.Entry(left_frame)
        self.ndbh_entry.grid(row=6, column=1, sticky="ew", pady=5)

        ttk.Label(left_frame, text="Khách hàng:").grid(row=7, column=0, sticky="w", pady=5)
        self.khach_hang_entry = ttk.Entry(left_frame)
        self.khach_hang_entry.grid(row=7, column=1, sticky="ew", pady=5)

        ttk.Label(left_frame, text="HLBH từ:").grid(row=8, column=0, sticky="w", pady=5)
        self.hlbh_tu_entry = DateEntry(left_frame, dateformat="%d/%m/%Y", bootstyle="primary")
        self.hlbh_tu_entry.grid(row=8, column=1, sticky="ew", pady=5)

        ttk.Label(left_frame, text="HLBH đến:").grid(row=9, column=0, sticky="w", pady=5)
        self.hlbh_den_entry = DateEntry(left_frame, dateformat="%d/%m/%Y", bootstyle="primary")
        self.hlbh_den_entry.grid(row=9, column=1, sticky="ew", pady=5)

        # --- Right Frame Widgets ---
        ttk.Label(right_frame, text="Ngày nhận hồ sơ:").grid(row=0, column=0, sticky="w", pady=5)
        self.ngay_nhan_hs_entry = DateEntry(right_frame, dateformat="%d/%m/%Y", bootstyle="primary")
        self.ngay_nhan_hs_entry.grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(right_frame, text="Ngày rủi ro:").grid(row=1, column=0, sticky="w", pady=5)
        self.ngay_rui_ro_entry = DateEntry(right_frame, dateformat="%d/%m/%Y", bootstyle="primary")
        self.ngay_rui_ro_entry.grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(right_frame, text="Số tiền yêu cầu:").grid(row=2, column=0, sticky="w", pady=5)
        self.so_tien_yc_entry = ttk.Entry(right_frame)
        self.so_tien_yc_entry.grid(row=2, column=1, sticky="ew", pady=5)
        self.so_tien_yc_entry.bind('<FocusOut>', self.format_currency)
        self.so_tien_yc_entry.bind('<FocusIn>', self.unformat_currency)

        ttk.Label(right_frame, text="Số tiền ước bồi thường:").grid(row=3, column=0, sticky="w", pady=5)
        self.so_tien_bt_entry = ttk.Entry(right_frame)
        self.so_tien_bt_entry.grid(row=3, column=1, sticky="ew", pady=5)
        self.so_tien_bt_entry.bind('<FocusOut>', self.format_currency)
        self.so_tien_bt_entry.bind('<FocusIn>', self.unformat_currency)

        ttk.Label(right_frame, text="Phòng giải quyết:").grid(row=4, column=0, sticky="w", pady=5)
        self.phong_gq_combo = ttk.Combobox(right_frame, state="readonly")
        self.phong_gq_combo.grid(row=4, column=1, sticky="ew", pady=5)
        self.phong_gq_combo.bind('<<ComboboxSelected>>', self.update_can_bo_dropdown)

        ttk.Label(right_frame, text="Cán bộ giải quyết:").grid(row=5, column=0, sticky="w", pady=5)
        self.can_bo_gq_combo = ttk.Combobox(right_frame, state="readonly")
        self.can_bo_gq_combo.grid(row=5, column=1, sticky="ew", pady=5)

        ttk.Label(right_frame, text="Loại bệnh:").grid(row=6, column=0, sticky="w", pady=5)
        self.loai_benh_combo = ttk.Combobox(right_frame, state="readonly")
        self.loai_benh_combo.grid(row=6, column=1, sticky="ew", pady=5)

        ttk.Label(right_frame, text="Tình trạng:").grid(row=7, column=0, sticky="w", pady=5)
        self.tinh_trang_combo = ttk.Combobox(right_frame, state="readonly")
        self.tinh_trang_combo.grid(row=7, column=1, sticky="ew", pady=5)

        ttk.Label(right_frame, text="Mô tả nguyên nhân:").grid(row=8, column=0, sticky="nw", pady=5)
        self.mo_ta_nn_text = Text(right_frame, height=5, width=40, wrap="word")
        self.mo_ta_nn_text.grid(row=8, column=1, sticky="nsew", pady=5)

        # --- Button Widgets (placed in button_frame defined above) ---
        save_button = ttk.Button(button_frame, text="Lưu thay đổi", command=self.save_changes, bootstyle=SUCCESS)
        save_button.pack(side="right")

    def load_initial_data(self):
        self.load_ban_dropdown()
        self.load_cttv_dropdown()
        self.load_phong_ban_dropdown()
        self.update_can_bo_dropdown() # Load initial list
        self.load_loai_benh_dropdown()
        self.load_tinh_trang_dropdown()

    def load_data(self):
        data = db_manager.get_ho_so_by_id(self.hs_id)
        if not data:
            Messagebox.show_error("Lỗi", f"Không tìm thấy hồ sơ với ID {self.hs_id}")
            return
        
        (hs_id, so_ho_so, ndbh, khach_hang, hlbh_tu, hlbh_den, ngay_rui_ro, ngay_nhan_hs, 
         so_tien_yc, so_tien_bt, tinh_trang_id, loai_benh_id, mo_ta_nn,
         cttv_id, san_pham_id, can_bo_id, so_the_bh, so_hd_bh, time_create,
         _ngay_bt, _hau_qua, _giai_quyet, _nguoi_duyet_id) = data

        self.so_gyctt_entry.config(state='normal')
        self.so_gyctt_entry.delete(0, 'end')
        self.so_gyctt_entry.insert(0, so_ho_so or "")
        self.so_gyctt_entry.config(state='readonly')

        self.ndbh_entry.delete(0, 'end'); self.ndbh_entry.insert(0, ndbh or "")
        self.khach_hang_entry.delete(0, 'end'); self.khach_hang_entry.insert(0, khach_hang or "")
        self.so_the_entry.delete(0, 'end'); self.so_the_entry.insert(0, so_the_bh or "")
        self.so_hd_entry.delete(0, 'end'); self.so_hd_entry.insert(0, so_hd_bh or "")
        self.so_tien_yc_entry.delete(0, 'end'); self.so_tien_yc_entry.insert(0, f"{so_tien_yc:,.0f}" if so_tien_yc is not None else "")
        self.so_tien_bt_entry.delete(0, 'end'); self.so_tien_bt_entry.insert(0, f"{so_tien_bt:,.0f}" if so_tien_bt is not None else "")
        self.mo_ta_nn_text.delete('1.0', 'end'); self.mo_ta_nn_text.insert('1.0', mo_ta_nn or "")

        def set_date_if_exists(date_entry, date_str):
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    date_entry.entry.delete(0, 'end')
                    date_entry.entry.insert(0, date_obj.strftime('%d/%m/%Y'))
                except (ValueError, TclError):
                    pass

        set_date_if_exists(self.hlbh_tu_entry, hlbh_tu)
        set_date_if_exists(self.hlbh_den_entry, hlbh_den)
        set_date_if_exists(self.ngay_nhan_hs_entry, ngay_nhan_hs)
        set_date_if_exists(self.ngay_rui_ro_entry, ngay_rui_ro)

        cttv_name = db_manager.get_name_by_id('CTTV', 'TenCTTV', 'CTTVID', cttv_id)
        self.cttv_combo.set(cttv_name or "")

        ban_name = db_manager.get_ban_name_by_san_pham_id(san_pham_id)
        if ban_name:
            self.ban_combo.set(ban_name)
            self.update_san_pham_dropdown()
            san_pham_name = db_manager.get_name_by_id('SanPham', 'TenSanPham', 'SanPhamID', san_pham_id)
            self.san_pham_combo.set(san_pham_name or "")

        phong_ban_name = db_manager.get_phong_ban_by_nhan_vien_id(can_bo_id)
        if phong_ban_name:
            self.phong_gq_combo.set(phong_ban_name)
            self.update_can_bo_dropdown()
            can_bo_name = db_manager.get_name_by_id('NhanVien', 'HoTen', 'NhanVienID', can_bo_id)
            self.can_bo_gq_combo.set(can_bo_name or "")
        
        loai_benh_name = db_manager.get_name_by_id('LoaiBenh', 'TenLoaiBenh', 'LoaiBenhID', loai_benh_id)
        self.loai_benh_combo.set(loai_benh_name or "")

        tinh_trang_name = db_manager.get_name_by_id('TinhTrangHoSo', 'TenTinhTrang', 'TinhTrangID', tinh_trang_id)
        self.tinh_trang_combo.set(tinh_trang_name or "")

    def _validate_date(self, date_str):
        try:
            if date_str:
                datetime.strptime(date_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    def save_changes(self):
        try:
            ndbh = self.ndbh_entry.get().strip()
            khach_hang = self.khach_hang_entry.get().strip()
            so_the_bh = self.so_the_entry.get().strip()
            so_hd_bh = self.so_hd_entry.get().strip()
            hlbh_tu_str = self.hlbh_tu_entry.entry.get().strip()
            hlbh_den_str = self.hlbh_den_entry.entry.get().strip()
            ngay_rui_ro_str = self.ngay_rui_ro_entry.entry.get().strip()
            ngay_nhan_hs_str = self.ngay_nhan_hs_entry.entry.get().strip()
            so_tien_yc_str = self.so_tien_yc_entry.get().replace(',', '')
            so_tien_bt_str = self.so_tien_bt_entry.get().replace(',', '')
            mo_ta_nn = self.mo_ta_nn_text.get("1.0", "end-1c").strip()

            cttv_cap_don = self.cttv_combo.get()
            san_pham = self.san_pham_combo.get()
            phong_gq = self.phong_gq_combo.get()
            can_bo_gq = self.can_bo_gq_combo.get()
            loai_benh = self.loai_benh_combo.get()
            tinh_trang = self.tinh_trang_combo.get()

            date_fields = {
                "HLBH từ": hlbh_tu_str, "HLBH đến": hlbh_den_str,
                "Ngày rủi ro": ngay_rui_ro_str, "Ngày nhận hồ sơ": ngay_nhan_hs_str
            }
            for field_name, date_str in date_fields.items():
                if date_str and not self._validate_date(date_str):
                    Messagebox.show_error("Lỗi định dạng ngày", f'Trường "{field_name}" không hợp lệ. Vui lòng dùng DD/MM/YYYY.')
                    return

            hlbh_tu = datetime.strptime(hlbh_tu_str, "%d/%m/%Y").date() if hlbh_tu_str else None
            hlbh_den = datetime.strptime(hlbh_den_str, "%d/%m/%Y").date() if hlbh_den_str else None
            ngay_rui_ro = datetime.strptime(ngay_rui_ro_str, "%d/%m/%Y").date() if ngay_rui_ro_str else None
            ngay_nhan_hs = datetime.strptime(ngay_nhan_hs_str, "%d/%m/%Y").date() if ngay_nhan_hs_str else None
            so_tien_yeu_cau = float(so_tien_yc_str) if so_tien_yc_str else None
            so_tien_boi_thuong = float(so_tien_bt_str) if so_tien_bt_str else None

            cttv_id = db_manager.get_id_by_name('CTTV', 'CTTVID', 'TenCTTV', cttv_cap_don)
            san_pham_id = db_manager.get_id_by_name('SanPham', 'SanPhamID', 'TenSanPham', san_pham)
            tinh_trang_id = db_manager.get_id_by_name('TinhTrangHoSo', 'TinhTrangID', 'TenTinhTrang', tinh_trang)
            loai_benh_id = db_manager.get_id_by_name('LoaiBenh', 'LoaiBenhID', 'TenLoaiBenh', loai_benh)
            can_bo_id = db_manager.get_id_by_name('NhanVien', 'NhanVienID', 'HoTen', can_bo_gq)
            # Ban ID is not stored, it's derived from SanPham. No need to get ID for it.

            data_tuple = (
                ndbh, khach_hang, 
                hlbh_tu.strftime('%Y-%m-%d') if hlbh_tu else None, 
                hlbh_den.strftime('%Y-%m-%d') if hlbh_den else None,
                ngay_rui_ro.strftime('%Y-%m-%d') if ngay_rui_ro else None, 
                ngay_nhan_hs.strftime('%Y-%m-%d') if ngay_nhan_hs else None,
                so_tien_yeu_cau, so_tien_boi_thuong, tinh_trang_id, loai_benh_id, mo_ta_nn,
                cttv_id, san_pham_id, can_bo_id, so_the_bh, so_hd_bh
            )

            if db_manager.update_ho_so(self.hs_id, data_tuple):
                Messagebox.show_info("Cập nhật hồ sơ thành công!","Thông báo" )
                if self.on_save_callback:
                    self.on_save_callback()
            else:
                Messagebox.show_error("Lỗi cơ sở dữ liệu", "Cập nhật hồ sơ thất bại.")

        except ValueError as e:
            Messagebox.show_error("Lỗi định dạng", f"Vui lòng kiểm tra lại định dạng ngày (DD/MM/YYYY) và các trường số. Lỗi: {e}")
        except Exception as e:
            Messagebox.show_error("Lỗi không xác định", f"Đã xảy ra lỗi khi lưu: {e}")

    def load_cttv_dropdown(self):
        cttv_list = [c[0] for c in db_manager.get_cttvs()]
        self.cttv_combo['values'] = cttv_list

    def load_phong_ban_dropdown(self):
        phong_ban_list = [p[0] for p in db_manager.get_phong_bans()]
        self.phong_gq_combo['values'] = phong_ban_list

    def update_can_bo_dropdown(self, event=None):
        phong_ban_name = self.phong_gq_combo.get()
        if phong_ban_name:
            can_bo_list = [c[0] for c in db_manager.get_can_bos_by_phong_ban(phong_ban_name)]
            self.can_bo_gq_combo['values'] = can_bo_list
            if not self.can_bo_gq_combo.get() in can_bo_list:
                 self.can_bo_gq_combo.set('')
        else:
            self.can_bo_gq_combo['values'] = []
            self.can_bo_gq_combo.set('')

    def load_loai_benh_dropdown(self):
        loai_benh_list = [lb[0] for lb in db_manager.get_loai_benhs()]
        self.loai_benh_combo['values'] = loai_benh_list

    def load_tinh_trang_dropdown(self):
        tinh_trang_list = [tt[0] for tt in db_manager.get_tinh_trang_ho_so()]
        self.tinh_trang_combo['values'] = tinh_trang_list

    def load_ban_dropdown(self):
        ban_list = [b[0] for b in db_manager.get_ban_cap_dons()]
        self.ban_combo['values'] = ban_list

    def update_san_pham_dropdown(self, event=None):
        ban_name = self.ban_combo.get()
        if ban_name:
            san_pham_list = [sp[0] for sp in db_manager.get_san_phams_by_ban(ban_name)]
            self.san_pham_combo['values'] = san_pham_list
            if not self.san_pham_combo.get() in san_pham_list:
                self.san_pham_combo.set('')
        else:
            self.san_pham_combo['values'] = []
            self.san_pham_combo.set('')

    def format_currency(self, event):
        try:
            value = event.widget.get().replace(',', '')
            if value:
                formatted_value = f"{float(value):,.0f}"
                event.widget.delete(0, 'end')
                event.widget.insert(0, formatted_value)
        except (ValueError, TclError):
            pass

    def unformat_currency(self, event):
        try:
            value = event.widget.get().replace(',', '')
            event.widget.delete(0, 'end')
            event.widget.insert(0, value)
        except TclError:
            pass
