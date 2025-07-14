import ttkbootstrap as ttk

class LapToTrinhFrame(ttk.Frame):
    def __init__(self, parent, hs_id):
        super().__init__(parent)
        self.hs_id = hs_id
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text=f"Lập tờ trình cho Hồ sơ ID: {self.hs_id}").pack(pady=20)
        # Giao diện lập tờ trình sẽ được xây dựng ở đây
