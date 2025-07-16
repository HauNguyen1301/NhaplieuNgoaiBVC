import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledText
from database import database_manager as db_manager
import datetime
from tkinter import TclError

class LapToTrinhFrame(ttk.Frame):
    def __init__(self, parent, hs_id, parent_app, on_save_callback=None):
        super().__init__(parent)
        self.hs_id = hs_id
        self.parent_app = parent_app
        self.on_save_callback = on_save_callback
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        form_frame = ttk.Frame(self)
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

        save_button = ttk.Button(self, text="Lưu tờ trình", command=self.save_to_trinh, bootstyle="success")
        save_button.pack(pady=20)

    def load_data(self):
        # Load NguoiDuyet combobox
        self.nhan_vien_list = db_manager.get_all_nhan_vien()
        self.entries["Người duyệt"]['values'] = [nv[1] for nv in self.nhan_vien_list]

        # Load TinhTrang combobox
        self.tinh_trang_list = db_manager.get_all_tinh_trang()
        self.entries["Tình trạng hồ sơ"]['values'] = [tt[1] for tt in self.tinh_trang_list]

        # Load existing HoSo data
        ho_so_data = db_manager.get_ho_so_by_id(self.hs_id)
        if ho_so_data:
            ngay_boi_thuong = ho_so_data[19]
            hau_qua = ho_so_data[20]
            giai_quyet = ho_so_data[21]
            so_tien_boi_thuong = ho_so_data[9]
            tinh_trang_id = ho_so_data[10]
            nguoi_duyet_id = ho_so_data[22]

            if ngay_boi_thuong:
                # DateEntry uses a different way to set date
                try:
                    # Assuming date from DB is dd/mm/yyyy
                    date_obj = datetime.datetime.strptime(ngay_boi_thuong, '%d/%m/%Y').date()
                    self.entries["Ngày bồi thường"].configure(startdate=date_obj)
                except (ValueError, TypeError):
                    # Fallback for different formats or None
                    self.entries["Ngày bồi thường"].entry.delete(0, 'end')
                    self.entries["Ngày bồi thường"].entry.insert(0, ngay_boi_thuong or "")

            self.entries["Hậu quả"].delete('1.0', 'end')
            self.entries["Hậu quả"].insert('1.0', hau_qua if hau_qua else "")
            
            self.entries["Giải quyết"].delete('1.0', 'end')
            self.entries["Giải quyết"].insert('1.0', giai_quyet if giai_quyet else "")

            # Format and insert currency
            so_tien_entry = self.entries["Số tiền bồi thường"]
            so_tien_entry.delete(0, 'end')
            if so_tien_boi_thuong is not None:
                try:
                    formatted_value = f"{float(so_tien_boi_thuong):,.0f}"
                    so_tien_entry.insert(0, formatted_value)
                except (ValueError, TypeError):
                    so_tien_entry.insert(0, so_tien_boi_thuong)
            
            # Set TinhTrang combobox
            if tinh_trang_id is not None:
                for i, tt in enumerate(self.tinh_trang_list):
                    if tt[0] == tinh_trang_id:
                        self.entries["Tình trạng hồ sơ"].current(i)
                        break
            
            # Set NguoiDuyet combobox
            if nguoi_duyet_id is not None:
                for i, nv in enumerate(self.nhan_vien_list):
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
            nguoi_duyet_id = self.nhan_vien_list[selected_nv_index][0] if selected_nv_index != -1 else None

            # Get TinhTrang ID
            selected_tt_index = self.entries["Tình trạng hồ sơ"].current()
            tinh_trang_id = self.tinh_trang_list[selected_tt_index][0] if selected_tt_index != -1 else None

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
