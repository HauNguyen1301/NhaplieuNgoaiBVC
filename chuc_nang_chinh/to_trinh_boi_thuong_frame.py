import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from database import database_manager as db_manager
from .edit_gyctt_frame import EditGYCTTFrame
from .lap_to_trinh_frame import LapToTrinhFrame


class ToTrinhBoiThuongFrame(ttk.Frame):
    def __init__(self, parent, parent_app):
        super().__init__(parent)
        self.parent = parent
        self.parent_app = parent_app
        self.create_widgets()

    def create_widgets(self):
        content_frame = self

        # --- Khung trên --- 
        frame_top_left = ttk.LabelFrame(content_frame, text="Tìm kiếm", padding=10)
        frame_top_left.place(relx=0, rely=0, relwidth=0.35, relheight=0.25)

        frame_top_right = ttk.LabelFrame(content_frame, text="Kết quả tìm kiếm", padding=10)
        frame_top_right.place(relx=0.35, rely=0, relwidth=0.65, relheight=0.25)

        # --- Khung dưới ---
        frame_bottom = ttk.LabelFrame(content_frame, text="Nội dung tờ trình", padding=10)
        frame_bottom.place(relx=0, rely=0.25, relwidth=1.0, relheight=0.75)

        # --- Widgets trong frame Tìm kiếm (top_left) ---
        self.setup_search_widgets(frame_top_left)

        # --- Widgets trong frame Kết quả (top_right) ---
        self.setup_results_treeview(frame_top_right)
        
        # --- Widgets trong frame Nội dung (bottom) ---
        self.setup_content_frame(frame_bottom)

    def setup_search_widgets(self, parent_frame):
        parent_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(parent_frame, text="Số hồ sơ:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.so_ho_so_entry = ttk.Entry(parent_frame)
        self.so_ho_so_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(parent_frame, text="Tên NĐBH:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.ten_ndbh_entry = ttk.Entry(parent_frame)
        self.ten_ndbh_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        search_button = ttk.Button(parent_frame, text="Tìm kiếm", command=self.perform_search, bootstyle="info")
        search_button.grid(row=2, column=1, padx=5, pady=10, sticky='e')

        self.so_ho_so_entry.bind('<Return>', lambda event: self.perform_search())
        self.ten_ndbh_entry.bind('<Return>', lambda event: self.perform_search())

    def setup_results_treeview(self, parent_frame):
        parent_frame.pack_propagate(False) # Ngăn frame co lại
        columns = ('id', 'so_ho_so', 'ten_ndbh', 'san_pham', 'tinh_trang')
        self.tree = ttk.Treeview(parent_frame, columns=columns, show='headings', height=5)

        self.tree.heading('id', text='ID')
        self.tree.heading('so_ho_so', text='Số hồ sơ')
        self.tree.heading('ten_ndbh', text='Người được bảo hiểm')
        self.tree.heading('san_pham', text='Sản phẩm')
        self.tree.heading('tinh_trang', text='Tình trạng')

        self.tree.column('id', width=40, anchor='center')
        self.tree.column('so_ho_so', width=120, anchor='center')
        self.tree.column('ten_ndbh', width=200, anchor='center')
        self.tree.column('san_pham', width=100, anchor='center')
        self.tree.column('tinh_trang', width=120, anchor='center')

        scrollbar = ttk.Scrollbar(parent_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def perform_search(self):
        so_ho_so = self.so_ho_so_entry.get().strip()
        ten_ndbh = self.ten_ndbh_entry.get().strip()

        if not so_ho_so and not ten_ndbh:
            Messagebox.show_warning("Thiếu thông tin", "Vui lòng nhập ít nhất một tiêu chí tìm kiếm.")
            return

        results = db_manager.search_ho_so(so_ho_so=so_ho_so, ten_ndbh=ten_ndbh)
        
        # Xóa kết quả cũ
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Thêm kết quả mới
        if not results:
            Messagebox.show_info("Không tìm thấy", "Không tìm thấy hồ sơ nào phù hợp.")
        else:
            for row in results:
                # Ensure row is a flat tuple/list for the values parameter
                self.tree.insert('', 'end', values=(row[0], row[1], row[2], row[3], row[4]))

        # Reset selection state after search
        self.selected_hs_id = None
        self.selected_info_label.config(text="Chưa chọn hồ sơ.")

    def setup_content_frame(self, parent_frame):
        self.selected_hs_id = None

        # Khung chứa các nút điều hướng
        button_container = ttk.Frame(parent_frame)
        button_container.pack(fill='x', padx=5, pady=5)

        edit_button = ttk.Button(button_container, text="Chỉnh sửa thông tin GYCTT", command=self.show_edit_gyctt_panel, bootstyle="primary")
        edit_button.pack(side='left', padx=5)

        create_trinh_button = ttk.Button(button_container, text="Lập tờ trình bồi thường", command=self.show_lap_to_trinh_panel, bootstyle="success")
        create_trinh_button.pack(side='left', padx=5)

        self.selected_info_label = ttk.Label(button_container, text="Chưa chọn hồ sơ.", bootstyle="info")
        self.selected_info_label.pack(side='left', padx=10)

        # Khung chính để hiển thị các panel con
        self.content_panel_container = ttk.Frame(parent_frame)
        self.content_panel_container.pack(fill='both', expand=True, padx=5, pady=5)

        # Label mặc định
        self.default_content_label = ttk.Label(self.content_panel_container, text="Vui lòng tìm và chọn một hồ sơ để thực hiện chức năng.", anchor='center')
        self.default_content_label.pack(fill='both', expand=True)

    def on_tree_select(self, event):
        selected_items = self.tree.selection()
        if selected_items:
            selected_item = selected_items[0]
            item_values = self.tree.item(selected_item, 'values')
            self.selected_hs_id = item_values[0]
            so_ho_so = item_values[1]
            ten_ndbh = item_values[2]
            self.selected_info_label.config(text=f"Đã chọn: {so_ho_so} - {ten_ndbh}")
        else:
            self.selected_hs_id = None
            self.selected_info_label.config(text="Chưa chọn hồ sơ.")

    def clear_content_panel(self):
        for widget in self.content_panel_container.winfo_children():
            widget.destroy()

    def show_edit_gyctt_panel(self):
        if not self.selected_hs_id:
            Messagebox.show_warning("Chưa chọn hồ sơ", "Vui lòng chọn một hồ sơ từ kết quả tìm kiếm.")
            return
        self.clear_content_panel()
        # Show new content
        on_save_and_close = lambda: (self.clear_content_panel(), self.perform_search())
        edit_frame = EditGYCTTFrame(self.content_panel_container, self.selected_hs_id, on_save_callback=on_save_and_close)
        edit_frame.pack(fill='both', expand=True)

    def show_lap_to_trinh_panel(self):
        if not self.selected_hs_id:
            Messagebox.show_warning("Chưa chọn hồ sơ", "Vui lòng chọn một hồ sơ từ kết quả tìm kiếm.")
            return

        self.clear_content_panel()

        # Define the callback function to be executed on successful save
        def on_save_callback():
            # Clear the panel where the form was displayed
            self.clear_content_panel()
            # Re-run the search to refresh the treeview with updated data
            self.perform_search()

        lap_to_trinh_frame = LapToTrinhFrame(
            self.content_panel_container,
            self.selected_hs_id,
            self.parent_app,
            on_save_callback=on_save_callback
        )
        lap_to_trinh_frame.pack(fill='both', expand=True)
