import tkinter as tk
from tkinter import ttk, Text, TclError
from datetime import datetime
import ttkbootstrap
from ttkbootstrap.constants import SUCCESS
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.scrolled import ScrolledFrame
import threading

from ttkbootstrap.dialogs import Messagebox
from database import database_manager as db_manager


class EditGYCTTFrame(ttk.Frame):
    def __init__(self, parent, hs_id, on_save_callback=None):
        super().__init__(parent)
        self.hs_id = hs_id
        self.on_save_callback = on_save_callback
        self.create_widgets()

        # Show loading indicator and load data in a background thread
        self.show_loading_indicator()
        threading.Thread(target=self._load_data_in_background, daemon=True).start()

    def create_widgets(self):
        content_frame = self

        # --- Main Layout ---
        # Frame for buttons, placed at the bottom
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(side='bottom', fill='x', padx=10, pady=10)

        # ScrolledFrame for the main content, placed above the buttons
        self.scroll_frame = ScrolledFrame(content_frame, autohide=True)
        self.scroll_frame.pack(side='top', fill='both', expand=True, padx=10, pady=(10, 0))

        # Use a PanedWindow to ensure two frames have equal width
        paned_window = ttk.PanedWindow(self.scroll_frame, orient='horizontal')
        paned_window.pack(fill='both', expand=True)

        # Main frames for content, placed inside the PanedWindow
        left_frame = ttk.LabelFrame(paned_window, text="Thông tin hồ sơ", padding=15)
        self.paned_window = paned_window
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

    def show_loading_indicator(self):
        self.loading_label = ttk.Label(self.scroll_frame, text="Đang tải dữ liệu, vui lòng chờ...", font=("Helvetica", 12))
        self.loading_label.pack(pady=50)

    def _load_data_in_background(self):
        try:
            # Fetch all data in the background
            self._ho_so_data = db_manager.get_ho_so_for_editing(self.hs_id)
            self._ban_list = [b[0] for b in db_manager.get_ban_cap_dons()]
            self._cttv_list = [c[0] for c in db_manager.get_cttvs()]
            self._phong_ban_list = [p[0] for p in db_manager.get_phong_bans()]
            self._loai_benh_list = [lb[0] for lb in db_manager.get_loai_benhs()]
            self._tinh_trang_list = [tt[0] for tt in db_manager.get_tinh_trang_ho_so()]

            # Schedule UI update on the main thread
            self.after(0, self._populate_ui)
        except Exception as e:
            self.after(0, lambda: Messagebox.show_error(f"Lỗi tải dữ liệu: {e}", "Lỗi"))

    def _populate_ui(self):
        # Remove loading indicator
        self.loading_label.destroy()

        # Populate dropdowns first
        self.ban_combo['values'] = self._ban_list
        self.cttv_combo['values'] = self._cttv_list
        self.phong_gq_combo['values'] = self._phong_ban_list
        self.loai_benh_combo['values'] = self._loai_benh_list
        self.tinh_trang_combo['values'] = self._tinh_trang_list

        # Now populate the form with the fetched data
        # Now populate the form with the fetched data
        self.load_data()

    def load_data(self):
        # Ensure data is not empty and is in the expected format (list of tuples)
        if not self._ho_so_data or not isinstance(self._ho_so_data, (list, tuple)) or not self._ho_so_data[0]:
            Messagebox.show_error("Không tìm thấy dữ liệu hồ sơ hoặc định dạng không hợp lệ.", "Lỗi dữ liệu")
            self.paned_window.pack_forget()
            return

        data = self._ho_so_data[0]  # Get the first record

        # Check if the record has the correct number of fields
        if len(data) != 17:
            Messagebox.show_error(f"Dữ liệu hồ sơ không đầy đủ. Mong đợi 17 trường nhưng nhận được {len(data)}.",
                                "Lỗi cấu trúc dữ liệu")
            self.paned_window.pack_forget()
            return

        try:
            # Unpack data
            (
                so_gyctt, ndbh, khach_hang, hlbh_tu, hlbh_den, ngay_rui_ro, ngay_nhan_hs,
                so_tien_yeu_cau, so_tien_boi_thuong, tinh_trang_id, loai_benh_id,
                mo_ta_nn, cttv_id, san_pham_id, can_bo_id, so_the, so_hd
            ) = data

            def set_date_if_exists(date_entry, date_str):
                if date_str:
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        date_entry.entry.delete(0, 'end')
                        date_entry.entry.insert(0, date_obj.strftime('%d/%m/%Y'))
                    except (ValueError, TypeError):
                        pass  # Ignore if date is invalid or None

            # Populate simple entry fields
            self.so_gyctt_entry.config(state='normal')
            self.so_gyctt_entry.delete(0, 'end')
            self.so_gyctt_entry.insert(0, so_gyctt or '')
            self.so_gyctt_entry.config(state='readonly')

            self.ndbh_entry.delete(0, 'end')
            self.ndbh_entry.insert(0, ndbh or '')
            self.khach_hang_entry.delete(0, 'end')
            self.khach_hang_entry.insert(0, khach_hang or '')
            self.so_the_entry.delete(0, 'end')
            self.so_the_entry.insert(0, so_the or '')
            self.so_hd_entry.delete(0, 'end')
            self.so_hd_entry.insert(0, so_hd or '')

            set_date_if_exists(self.hlbh_tu_entry, hlbh_tu)
            set_date_if_exists(self.hlbh_den_entry, hlbh_den)
            set_date_if_exists(self.ngay_rui_ro_entry, ngay_rui_ro)
            set_date_if_exists(self.ngay_nhan_hs_entry, ngay_nhan_hs)

            self.so_tien_yc_entry.delete(0, 'end')
            self.so_tien_yc_entry.insert(0, f"{so_tien_yeu_cau:,.0f}" if so_tien_yeu_cau is not None else '')
            self.so_tien_bt_entry.delete(0, 'end')
            self.so_tien_bt_entry.insert(0, f"{so_tien_boi_thuong:,.0f}" if so_tien_boi_thuong is not None else '')

            self.mo_ta_nn_text.delete('1.0', 'end')
            self.mo_ta_nn_text.insert('1.0', mo_ta_nn or '')

            # Populate comboboxes by finding the name from ID
            cttv_name = db_manager.get_name_by_id('CTTV', 'TenCTTV', 'CTTVID', cttv_id)
            self.cttv_combo.set(cttv_name or '')

            tinh_trang_name = db_manager.get_name_by_id('TinhTrangHoSo', 'TenTinhTrang', 'TinhTrangID', tinh_trang_id)
            self.tinh_trang_combo.set(tinh_trang_name or '')

            loai_benh_name = db_manager.get_name_by_id('LoaiBenh', 'TenLoaiBenh', 'LoaiBenhID', loai_benh_id)
            self.loai_benh_combo.set(loai_benh_name or '')

            # For nested dropdowns, we need to set the parent first, then trigger the update, then set the child
            ban_name = db_manager.get_ban_name_by_san_pham_id(san_pham_id)
            if ban_name:
                self.ban_combo.set(ban_name)
                self.update_san_pham_dropdown()  # This will populate the san_pham_combo
                san_pham_name = db_manager.get_name_by_id('SanPham', 'TenSanPham', 'SanPhamID', san_pham_id)
                self.san_pham_combo.set(san_pham_name or '')

            phong_ban_name = db_manager.get_phong_ban_by_nhan_vien_id(can_bo_id)
            if phong_ban_name:
                self.phong_gq_combo.set(phong_ban_name)
                self.update_can_bo_dropdown()  # This will populate the can_bo_gq_combo
                can_bo_name = db_manager.get_name_by_id('NhanVien', 'HoTen', 'NhanVienID', can_bo_id)
                self.can_bo_gq_combo.set(can_bo_name or '')

        except (ValueError, IndexError) as e:
            Messagebox.show_error(f"Không thể xử lý dữ liệu hồ sơ: {e}", "Lỗi dữ liệu")
            self.paned_window.pack_forget()

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
