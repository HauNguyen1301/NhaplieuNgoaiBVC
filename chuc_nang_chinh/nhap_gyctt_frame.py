import tkinter as tk
from tkinter import ttk, Text, TclError
from datetime import datetime
import ttkbootstrap
from ttkbootstrap.constants import SUCCESS
from ttkbootstrap.widgets import DateEntry
import threading

from ttkbootstrap.dialogs import Messagebox
from database import database_manager as db_manager


class NhapGycttFrame(ttk.Frame):
    def __init__(self, parent, user_info):
        super().__init__(parent)
        self.user_info = user_info
        self.create_widgets()
        # Load data in a separate thread to avoid blocking the UI
        threading.Thread(target=self.load_initial_data, daemon=True).start()

    def create_widgets(self):
        content_frame = self

        # Main frames
        left_frame = ttk.LabelFrame(content_frame, text="Thông tin hồ sơ", padding=15)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        right_frame = ttk.LabelFrame(content_frame, text="Sự kiện bảo hiểm", padding=(10, 10))
        right_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        
        # Configure grid weights for resizing
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        left_frame.grid_columnconfigure(1, weight=1)
        right_frame.grid_columnconfigure(1, weight=1)
        right_frame.rowconfigure(4, weight=1) # Allow textarea to expand

        # --- Left Frame Widgets ---
        ttk.Label(left_frame, text="Ban cấp đơn:").grid(row=0, column=0, sticky="w", pady=5)
        self.ban_var = tk.StringVar()
        self.ban_options_frame = ttk.Frame(left_frame)
        self.ban_options_frame.grid(row=0, column=1, sticky="w", pady=5)
        # Initially show a loading message
        self.loading_bans_label = ttk.Label(self.ban_options_frame, text="Đang tải...")
        self.loading_bans_label.pack(side="left", padx=5)

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
        self.so_gyctt_entry = ttk.Entry(left_frame)
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

        ttk.Label(right_frame, text="Loại bệnh:").grid(row=3, column=0, sticky="w", pady=5)
        self.loai_benh_combo = ttk.Combobox(right_frame, state="readonly")
        self.loai_benh_combo.grid(row=3, column=1, sticky="ew", pady=5)

        ttk.Label(right_frame, text="Mô tả nguyên nhân:").grid(row=4, column=0, sticky="nw", pady=5)
        self.mo_ta_nn_text = Text(right_frame, height=5, width=40)
        self.mo_ta_nn_text.grid(row=4, column=1, sticky="nsew", pady=5)

        ttk.Label(right_frame, text="Tình trạng:").grid(row=5, column=0, sticky="w", pady=5)
        self.tinh_trang_combo = ttk.Combobox(right_frame, state="readonly")
        self.tinh_trang_combo.grid(row=5, column=1, sticky="ew", pady=5)

        ttk.Label(right_frame, text="Số tiền ước bồi thường:").grid(row=6, column=0, sticky="w", pady=5)
        self.so_tien_bt_entry = ttk.Entry(right_frame)
        self.so_tien_bt_entry.grid(row=6, column=1, sticky="ew", pady=5)
        self.so_tien_bt_entry.bind("<FocusOut>", self.format_currency)
        self.so_tien_bt_entry.bind("<FocusIn>", self.unformat_currency)

        ttk.Label(right_frame, text="Phòng giải quyết:").grid(row=7, column=0, sticky="w", pady=5)
        self.phong_gq_combo = ttk.Combobox(right_frame, state="readonly")
        self.phong_gq_combo.grid(row=7, column=1, sticky="ew", pady=5)
        self.phong_gq_combo.bind("<<ComboboxSelected>>", self.update_can_bo_dropdown)

        ttk.Label(right_frame, text="Cán bộ giải quyết:").grid(row=8, column=0, sticky="w", pady=5)
        self.can_bo_gq_combo = ttk.Combobox(right_frame, state="readonly")
        self.can_bo_gq_combo.grid(row=8, column=1, sticky="ew", pady=5)
        
        # --- Bottom Buttons ---
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        save_button = ttk.Button(button_frame, text="Lưu", command=self.save_data, bootstyle="success")
        save_button.pack(side="left", padx=10)

        clear_button = ttk.Button(button_frame, text="Xóa form", command=self.clear_form, bootstyle="warning")
        clear_button.pack(side="left", padx=10)

    def load_initial_data(self):
        """Tải tất cả dữ liệu ban đầu trong một thread riêng biệt."""
        try:
            # Fetch all data in one go
            bans = db_manager.get_ban_cap_dons()
            cttvs = db_manager.get_cttvs()
            phong_bans = db_manager.get_phong_bans()
            loai_benhs = db_manager.get_loai_benhs()
            tinh_trangs = db_manager.get_tinh_trang_ho_so()

            # Schedule UI updates on the main thread
            self.after(0, self.populate_ui, bans, cttvs, phong_bans, loai_benhs, tinh_trangs)
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu ban đầu: {e}")
            self.after(0, self.show_loading_error)

    def show_loading_error(self):
        self.loading_bans_label.config(text="Lỗi tải dữ liệu")
        # You can also show a messagebox or disable the form

    def populate_ui(self, bans, cttvs, phong_bans, loai_benhs, tinh_trangs):
        """Điền dữ liệu vào các widget UI sau khi đã tải xong."""
        # Populate Ban cap don radio buttons
        self.loading_bans_label.destroy()
        for ban in bans:
            ttk.Radiobutton(self.ban_options_frame, text=ban[0], variable=self.ban_var, value=ban[0], command=self.update_san_pham_dropdown).pack(side="left", padx=5)
        if bans:
            self.ban_var.set(bans[0][0])

        # Populate other comboboxes
        self.cttv_combo['values'] = [cttv[0] for cttv in cttvs]
        self.phong_gq_combo['values'] = [pb[0] for pb in phong_bans]
        self.loai_benh_combo['values'] = [lb[0] for lb in loai_benhs]
        self.tinh_trang_combo['values'] = [tt[0] for tt in tinh_trangs]

        # Set default values if lists are not empty
        if cttvs: self.cttv_combo.set(cttvs[0][0])
        if phong_bans: self.phong_gq_combo.set(phong_bans[0][0])
        if loai_benhs: self.loai_benh_combo.set(loai_benhs[0][0])
        if tinh_trangs: self.tinh_trang_combo.set(tinh_trangs[0][0])

        # Trigger dependent dropdown updates
        self.update_san_pham_dropdown()
        self.update_can_bo_dropdown()
        self.load_cttv_dropdown()

    def load_cttv_dropdown(self):
        cttvs = db_manager.get_cttvs()
        cttv_list = [c[0] for c in cttvs] if cttvs else []
        self.cttv_combo['values'] = cttv_list
        if cttv_list:
            self.cttv_combo.current(0)

    def update_can_bo_dropdown(self, event=None):
        selected_phong_ban = self.phong_gq_combo.get()
        if selected_phong_ban:
            # This still needs to be dynamic, so we can fetch it on demand
            # or pre-fetch all possible can_bos if the list is small.
            # For now, let's fetch it in a thread to avoid blocking on change.
            threading.Thread(target=self._load_can_bos, args=(selected_phong_ban,), daemon=True).start()

    def _load_can_bos(self, phong_ban):
        can_bos = db_manager.get_can_bos_by_phong_ban(phong_ban)
        self.after(0, self._populate_can_bos, can_bos)

    def _populate_can_bos(self, can_bos):
        self.can_bo_gq_combo['values'] = [cb[0] for cb in can_bos]
        if can_bos:
            self.can_bo_gq_combo.set(can_bos[0][0])
        else:
            self.can_bo_gq_combo.set('')

    def update_san_pham_dropdown(self, event=None):
        selected_ban = self.ban_var.get()
        if selected_ban:
            self.san_pham_combo.set('Đang tải...')
            threading.Thread(target=self._load_san_phams, args=(selected_ban,), daemon=True).start()
        else:
            self.san_pham_combo['values'] = []
            self.san_pham_combo.set('')

    def _load_san_phams(self, ban_cap_don):
        san_phams = db_manager.get_san_phams_by_ban(ban_cap_don)
        self.after(0, self._populate_san_phams, san_phams)

    def _populate_san_phams(self, san_phams):
        formatted_values = [f"{sp[0]} - {sp[1]}" for sp in san_phams]
        self.san_pham_combo['values'] = formatted_values
        if formatted_values:
            self.san_pham_combo.set(formatted_values[0])
        else:
            self.san_pham_combo.set('')
            self.san_pham_combo.config(state="disabled")

    def format_currency(self, event):
        widget = event.widget
        try:
            value = widget.get().replace(',', '')
            if value:
                formatted_value = f"{int(value):,}"
                widget.delete(0, 'end')
                widget.insert(0, formatted_value)
        except (ValueError, TclError):
            pass # Ignore formatting errors

    def unformat_currency(self, event):
        widget = event.widget
        try:
            value = widget.get().replace(',', '')
            widget.delete(0, 'end')
            widget.insert(0, value)
        except (ValueError, TclError):
            pass # Ignore unformatting errors



    def clear_form(self):
        """Clear all entry and text widgets after user confirmation."""
        if Messagebox.yesno("Are you sure you want to clear the form?", "Confirm") == "Yes":
            self.so_gyctt_entry.delete(0, tk.END)
            self.ndbh_entry.delete(0, tk.END)
            self.khach_hang_entry.delete(0, tk.END)
            self.so_tien_yc_entry.delete(0, tk.END)
            self.so_tien_bt_entry.delete(0, tk.END)
            self.mo_ta_nn_text.delete('1.0', tk.END)
            self.so_the_entry.delete(0, tk.END)
            self.so_hd_entry.delete(0, tk.END)
            # Reset comboboxes to the first item
            self.load_initial_data()

    def save_data(self):
        # --- Lấy dữ liệu từ form ---
        ban_cap_don = self.ban_var.get()
        san_pham = self.san_pham_combo.get()
        cttv_cap_don = self.cttv_combo.get()
        so_the_bh = self.so_the_entry.get().strip()
        so_hd_bh = self.so_hd_entry.get().strip()
        so_gyctt = self.so_gyctt_entry.get().strip()
        ndbh = self.ndbh_entry.get().strip()
        khach_hang = self.khach_hang_entry.get().strip()
        hlbh_tu_str = self.hlbh_tu_entry.entry.get().strip()
        hlbh_den_str = self.hlbh_den_entry.entry.get().strip()
        phong_gq = self.phong_gq_combo.get()
        can_bo_gq = self.can_bo_gq_combo.get()
        ngay_nhan_hs_str = self.ngay_nhan_hs_entry.entry.get().strip()
        ngay_rui_ro_str = self.ngay_rui_ro_entry.entry.get().strip()
        so_tien_yc_str = self.so_tien_yc_entry.get().replace(',', '')
        so_tien_bt_str = self.so_tien_bt_entry.get().replace(',', '')
        loai_benh = self.loai_benh_combo.get()
        tinh_trang = self.tinh_trang_combo.get()
        mo_ta_nn = self.mo_ta_nn_text.get('1.0', 'end-1c').strip()

        # --- Validate tình trạng hồ sơ ---
        if tinh_trang == "Đã giải quyết / Đã duyệt":
            Messagebox.show_error(title="Lỗi nghiệp vụ", message="Nhập GYCTT không thể chọn hồ sơ 'Đã giải quyết / Đã duyệt'.", parent=self)
            return

        # --- Validate các trường bắt buộc ---
        required_fields = {
            "Ban cấp đơn": ban_cap_don, "Sản phẩm": san_pham, "Công ty thành viên": cttv_cap_don,
            "Số thẻ bảo hiểm": so_the_bh, "Số hợp đồng bảo hiểm": so_hd_bh, "Người được bảo hiểm": ndbh,
            "Số GYCTT": so_gyctt, "Khách hàng": khach_hang,
            "HLBH từ": hlbh_tu_str, "HLBH đến": hlbh_den_str,
            "Phòng giải quyết": phong_gq, "Cán bộ giải quyết": can_bo_gq,
            "Ngày nhận hồ sơ": ngay_nhan_hs_str, "Ngày rủi ro": ngay_rui_ro_str,
            "Số tiền yêu cầu": so_tien_yc_str, "Loại bệnh": loai_benh, "Tình trạng": tinh_trang
        }
        missing_fields = [name for name, value in required_fields.items() if not value]
        if missing_fields:
            Messagebox.show_warning(title="Thiếu thông tin", message=f"Vui lòng điền đầy đủ các trường sau:\n- {', '.join(missing_fields)}", parent=self)
            return

        # --- Validate và chuyển đổi dữ liệu ---
        try:
            hlbh_tu = datetime.strptime(hlbh_tu_str, "%d/%m/%Y").date() if hlbh_tu_str else None
            hlbh_den = datetime.strptime(hlbh_den_str, "%d/%m/%Y").date() if hlbh_den_str else None
            ngay_rui_ro = datetime.strptime(ngay_rui_ro_str, "%d/%m/%Y").date() if ngay_rui_ro_str else None
            ngay_nhan_hs = datetime.strptime(ngay_nhan_hs_str, "%d/%m/%Y").date() if ngay_nhan_hs_str else None
            ngay_hien_tai = datetime.now().date()
            so_tien_yeu_cau = float(so_tien_yc_str) if so_tien_yc_str else 0
            so_tien_boi_thuong = float(so_tien_bt_str) if so_tien_bt_str else 0
        except ValueError as e:
            Messagebox.show_error(title="Lỗi định dạng dữ liệu", message=f"Dữ liệu nhập vào không hợp lệ. Vui lòng kiểm tra lại ngày tháng (DD/MM/YYYY) và số tiền.", parent=self)
            return

        # --- Validate logic ngày tháng ---
        if hlbh_tu >= hlbh_den:
            Messagebox.show_error(title="Lỗi logic ngày", message="'HLBH từ' phải trước 'HLBH đến'.", parent=self)
            return
        if not (hlbh_tu <= ngay_rui_ro <= hlbh_den):
            Messagebox.show_error(title="Lỗi logic ngày", message="Ngày rủi ro phải nằm trong thời hạn hiệu lực bảo hiểm.", parent=self)
            return
        if ngay_rui_ro >= ngay_nhan_hs:
            Messagebox.show_error(title="Lỗi logic ngày", message="Ngày rủi ro phải xảy ra trước Ngày nhận hồ sơ.", parent=self)
            return
        if ngay_rui_ro >= ngay_hien_tai or ngay_nhan_hs > ngay_hien_tai:
            Messagebox.show_error(title="Lỗi logic ngày", message="Ngày rủi ro và ngày nhận hồ sơ không được là ngày tương lai.", parent=self)
            return

        # --- Lưu vào cơ sở dữ liệu ---
        try:
            cttv_id = db_manager.get_id_by_name('CTTV', 'CTTVID', 'TenCTTV', cttv_cap_don)
            san_pham_id = db_manager.get_id_by_name('SanPham', 'SanPhamID', 'TenSanPham', san_pham)
            tinh_trang_id = db_manager.get_id_by_name('TinhTrangHoSo', 'TinhTrangID', 'TenTinhTrang', tinh_trang)
            loai_benh_id = db_manager.get_id_by_name('LoaiBenh', 'LoaiBenhID', 'TenLoaiBenh', loai_benh)
            can_bo_id = db_manager.get_id_by_name('NhanVien', 'NhanVienID', 'HoTen', can_bo_gq)

            if not all([cttv_id, san_pham_id, tinh_trang_id, loai_benh_id, can_bo_id]):
                Messagebox.show_error(title="Lỗi dữ liệu", message="Không thể tìm thấy ID cho một trong các giá trị đã chọn. Vui lòng kiểm tra lại.", parent=self)
                return

            # Lấy UserID từ user_info
            created_by_id = self.user_info[0]

            data_tuple = (
                so_gyctt, ndbh, khach_hang, hlbh_tu.strftime('%Y-%m-%d'), hlbh_den.strftime('%Y-%m-%d'), 
                ngay_rui_ro.strftime('%Y-%m-%d'), ngay_nhan_hs.strftime('%Y-%m-%d'), so_tien_yeu_cau, so_tien_boi_thuong, tinh_trang_id, loai_benh_id, 
                mo_ta_nn, cttv_id, san_pham_id, can_bo_id, so_the_bh, so_hd_bh, created_by_id
            )
            
            if db_manager.insert_gyctt(data_tuple):
                Messagebox.show_info(title="Thông báo", message="Lưu hồ sơ thành công!", parent=self)
                self.clear_form()
            else:
                Messagebox.show_error(title="Lỗi cơ sở dữ liệu", message="Lưu hồ sơ thất bại.", parent=self)

        except Exception as e:
            Messagebox.show_error(title="Lỗi không xác định", message=f"Đã xảy ra lỗi khi lưu: {e}", parent=self)
