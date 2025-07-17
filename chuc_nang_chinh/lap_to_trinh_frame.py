import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledText
from database import database_manager as db_manager
import datetime
import threading
from tkinter import TclError


class LapToTrinhFrame(ttk.Frame):
    def __init__(self, parent, hs_id, parent_app, on_save_callback=None):
        super().__init__(parent)
        self.hs_id = hs_id
        self.parent_app = parent_app
        self.on_save_callback = on_save_callback
        self.create_widgets()
        self.show_loading_indicator()
        threading.Thread(target=self._load_data_in_background, daemon=True).start()

    def create_widgets(self):
        content_frame = self
        form_frame = ttk.Frame(content_frame)
        form_frame.pack(fill='x', padx=20, pady=10)

        # Configure DateEntry with dd/mm/yyyy format
        ngay_boi_thuong_entry = DateEntry(form_frame, bootstyle="primary", dateformat="%d/%m/%Y")
        
        # Use ScrolledText for multi-line input
        hau_qua_text = ScrolledText(form_frame, height=3, wrap="word")
        giai_quyet_text = ScrolledText(form_frame, height=3, wrap="word")

        # Standard Entry for currency, with event binding
        so_tien_boi_thuong_entry = ttk.Entry(form_frame)
        so_tien_boi_thuong_entry.bind("<FocusOut>", self.format_currency)
        so_tien_boi_thuong_entry.bind("<FocusIn>", self.unformat_currency)

        fields = {
            "Ngày bồi thường:": ngay_boi_thuong_entry,
            "Hậu quả:": hau_qua_text,
            "Giải quyết:": giai_quyet_text,
            "Số tiền bồi thường:": so_tien_boi_thuong_entry,
            "Người duyệt:": ttk.Combobox(form_frame, state="readonly"),
            "Tình trạng hồ sơ:": ttk.Combobox(form_frame, state="readonly")
        }

        self.entries = {}
        for i, (label_text, widget) in enumerate(fields.items()):
            label = ttk.Label(form_frame, text=label_text)
            # Adjust sticky for ScrolledText to align label to the top-west
            label.grid(row=i, column=0, padx=5, pady=5, sticky='nw' if isinstance(widget, ScrolledText) else 'w')
            widget.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
            self.entries[label_text.replace(":", "").strip()] = widget

        form_frame.grid_columnconfigure(1, weight=1)

        self.save_button = ttk.Button(content_frame, text="Lưu tờ trình", command=self.save_to_trinh, bootstyle="success")
        self.save_button.pack(pady=20)
        self.save_button.config(state="disabled") # Disable until data is loaded

    def show_loading_indicator(self):
        self.loading_label = ttk.Label(self, text="Đang tải dữ liệu tờ trình...", font=("Helvetica", 12))
        self.loading_label.pack(pady=50)

    def _load_data_in_background(self):
        try:
            self._nhan_vien_list = db_manager.get_all_nhan_vien()
            self._tinh_trang_list = db_manager.get_all_tinh_trang()
            # Use the specific function for this frame
            self._ho_so_data = db_manager.get_ho_so_for_to_trinh(self.hs_id)
            self.after(0, self._populate_ui)
        except Exception as e:
            self.after(0, lambda: Messagebox.show_error(f"Lỗi tải dữ liệu: {e}", "Lỗi"))

    def _populate_ui(self):
        if not self.winfo_exists():
            return

        self.loading_label.destroy()
        self.save_button.config(state="normal")

        # Load dropdowns regardless of ho_so_data
        self.entries["Người duyệt"]['values'] = [nv[1] for nv in self._nhan_vien_list]
        self.entries["Tình trạng hồ sơ"]['values'] = [tt[1] for tt in self._tinh_trang_list]

        if not self._ho_so_data or not self._ho_so_data[0]:
            # No specific record data, but UI is ready
            return

        # Unpack data with correct indices from get_ho_so_for_to_trinh
        record = self._ho_so_data[0]
        if record:
            so_tien_boi_thuong, tinh_trang_id, ngay_boi_thuong_str, hau_qua, giai_quyet, nguoi_duyet_id = record

            if ngay_boi_thuong_str:
                try:
                    date_obj = datetime.datetime.strptime(ngay_boi_thuong_str, '%Y-%m-%d').date()
                    self.entries["Ngày bồi thường"].entry.delete(0, 'end')
                    self.entries["Ngày bồi thường"].entry.insert(0, date_obj.strftime('%d/%m/%Y'))
                except (ValueError, TypeError):
                    self.entries["Ngày bồi thường"].entry.delete(0, 'end')
                    self.entries["Ngày bồi thường"].entry.insert(0, ngay_boi_thuong_str or "")

            self.entries["Hậu quả"].delete('1.0', 'end')
            self.entries["Hậu quả"].insert('1.0', hau_qua if hau_qua else "")
            
            self.entries["Giải quyết"].delete('1.0', 'end')
            self.entries["Giải quyết"].insert('1.0', giai_quyet if giai_quyet else "")

            so_tien_entry = self.entries["Số tiền bồi thường"]
            so_tien_entry.delete(0, 'end')
            if so_tien_boi_thuong is not None:
                so_tien_entry.insert(0, f"{float(so_tien_boi_thuong):,.0f}")
            
            if tinh_trang_id is not None:
                for i, tt in enumerate(self._tinh_trang_list):
                    if tt[0] == tinh_trang_id:
                        self.entries["Tình trạng hồ sơ"].current(i)
                        break
            
            if nguoi_duyet_id is not None:
                for i, nv in enumerate(self._nhan_vien_list):
                    if nv[0] == nguoi_duyet_id:
                        self.entries["Người duyệt"].current(i)
                        break

    def save_to_trinh(self):
        try:
            ngay_boi_thuong = self.entries["Ngày bồi thường"].entry.get()
            hau_qua = self.entries["Hậu quả"].get('1.0', 'end-1c')
            giai_quyet = self.entries["Giải quyết"].get('1.0', 'end-1c')
            
            # Unformat currency before converting to float
            so_tien_str = self.entries["Số tiền bồi thường"].get().replace(',', '')
            so_tien_boi_thuong = float(so_tien_str or 0)

            # Get NguoiDuyet ID
            selected_nv_index = self.entries["Người duyệt"].current()
            nguoi_duyet_id = self._nhan_vien_list[selected_nv_index][0] if selected_nv_index != -1 else None

            # Get TinhTrang ID
            selected_tt_index = self.entries["Tình trạng hồ sơ"].current()
            tinh_trang_id = self._tinh_trang_list[selected_tt_index][0] if selected_tt_index != -1 else None

            # Lấy NhanVienID từ tuple current_user (index 4)
            can_bo_id = self.parent_app.current_user[4]
            time_update = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            data_tuple = (
                ngay_boi_thuong, hau_qua, giai_quyet, so_tien_boi_thuong,
                nguoi_duyet_id, tinh_trang_id, can_bo_id, time_update
            )

            if db_manager.update_to_trinh(self.hs_id, data_tuple):
                Messagebox.show_info("Thành công", "Lưu tờ trình thành công!")
                if self.on_save_callback:
                    self.on_save_callback()
            else:
                Messagebox.show_error("Lỗi", "Không thể cập nhật tờ trình.")

        except ValueError:
            Messagebox.show_error("Lỗi", "Số tiền bồi thường không hợp lệ. Vui lòng chỉ nhập số.")
        except Exception as e:
            Messagebox.show_error("Lỗi", f"Đã xảy ra lỗi: {e}")

    def format_currency(self, event):
        try:
            value = event.widget.get().replace(',', '')
            if value:
                formatted_value = f"{float(value):,.0f}"
                event.widget.delete(0, 'end')
                event.widget.insert(0, formatted_value)
        except (ValueError, TclError):
            pass # Ignore formatting errors

    def unformat_currency(self, event):
        try:
            value = event.widget.get().replace(',', '')
            event.widget.delete(0, 'end')
            event.widget.insert(0, value)
        except (ValueError, TclError):
            pass # Ignore unformatting errors
