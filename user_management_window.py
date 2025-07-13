import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import sqlite3
from database import execute_query, insert_data, update_data

class UserManagementWindow(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent, "Quản lý người dùng")
        self.geometry("800x500")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x", pady=(0, 10))

        search_label = ttk.Label(top_frame, text="Tìm kiếm:")
        search_label.pack(side=LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(top_frame)
        self.search_entry.pack(side=LEFT, fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_users)

        button_frame = ttk.Frame(top_frame)
        button_frame.pack(side=RIGHT)
        
        add_button = ttk.Button(button_frame, text="Thêm mới", command=self.add_user, bootstyle=SUCCESS)
        add_button.pack(side='left', padx=(0, 5))


        
        change_pass_button = ttk.Button(button_frame, text="Đổi mật khẩu", command=self.change_user_password, bootstyle=WARNING)
        change_pass_button.pack(side=LEFT, padx=5)

        change_role_button = ttk.Button(button_frame, text="Đổi vai trò", command=self.change_user_role, bootstyle=INFO)
        change_role_button.pack(side=LEFT)


        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True)

        columns = ("UserID", "Username", "Role", "HoTen", "HR_PhongBan")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Define column headings
        self.tree.heading("UserID", text="User ID")
        self.tree.heading("Username", text="Tên đăng nhập")
        self.tree.heading("Role", text="Vai trò")
        self.tree.heading("HoTen", text="Họ và tên")
        self.tree.heading("HR_PhongBan", text="Phòng ban")

        # Define column properties
        self.tree.column("UserID", width=80, anchor='center')
        self.tree.column("Username", width=150, anchor='center')
        self.tree.column("Role", width=100, anchor='center')
        self.tree.column("HoTen", width=200, anchor='center')
        self.tree.column("HR_PhongBan", width=150, anchor='center')
        
        self.tree.pack(side=LEFT, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill="y")

    def load_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            query = """
                SELECT u.UserID, u.Username, u.Role, n.HoTen, n.HR_PhongBan
                FROM User u
                LEFT JOIN NhanVien n ON u.NhanVienID = n.NhanVienID
                ORDER BY u.UserID
            """
            users = execute_query(query)
            
            if users:
                for user in users:
                    # Replace None with empty string for better display
                    display_values = [v if v is not None else "" for v in user]
                    self.tree.insert("", "end", values=display_values)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách người dùng: {e}", parent=self)

    def filter_users(self, event=None):
        search_term = self.search_entry.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if hasattr(self, 'all_users'):
            for user in self.all_users:
                if search_term in str(user[1]).lower(): # Search by username
                    self.tree.insert("", "end", values=user)

    def get_selected_user(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một người dùng từ danh sách.", parent=self)
            return None
        user_data = self.tree.item(selected_item)['values']
        self.selected_user_label.config(text=f"Đã chọn: {user_data[1]}")
        return user_data

    def add_user(self):
        add_window = ttk.Toplevel(self, "Thêm người dùng mới")
        add_window.geometry("400x450")
        add_window.transient(self)
        add_window.grab_set()

        employee_map = {}

        def load_departments_for_add_window():
            try:
                conn = sqlite3.connect('boithuong.db')
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT HR_PhongBan FROM NhanVien WHERE HR_PhongBan IS NOT NULL ORDER BY HR_PhongBan")
                departments = [row[0] for row in cursor.fetchall()]
                conn.close()
                department_combobox['values'] = departments
                if departments:
                    department_combobox.current(0)
                    load_employees_for_add_window()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tải danh sách phòng ban: {e}", parent=add_window)

        def load_employees_for_add_window(event=None):
            department = department_combobox.get()
            if not department:
                return
            
            try:
                conn = sqlite3.connect('boithuong.db')
                cursor = conn.cursor()
                cursor.execute("SELECT NhanVienID, HoTen FROM NhanVien WHERE HR_PhongBan = ? ORDER BY HoTen", (department,))
                employees = cursor.fetchall()
                conn.close()
                
                employee_map.clear()
                employee_combobox['values'] = []
                
                employee_names = []
                for nhanvien_id, hoten in employees:
                    employee_map[hoten] = nhanvien_id
                    employee_names.append(hoten)
                
                employee_combobox['values'] = employee_names
                if employee_names:
                    employee_combobox.current(0)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tải danh sách nhân viên: {e}", parent=add_window)

        ttk.Label(add_window, text="Tên đăng nhập:").pack(pady=(10, 0))
        username_entry = ttk.Entry(add_window)
        username_entry.pack(pady=5, padx=20, fill='x')

        ttk.Label(add_window, text="Mật khẩu:").pack(pady=(10, 0))
        password_entry = ttk.Entry(add_window, show="*")
        password_entry.pack(pady=5, padx=20, fill='x')

        ttk.Label(add_window, text="Vai trò:").pack(pady=(10, 0))
        role_combobox = ttk.Combobox(add_window, values=["admin", "user"], state="readonly")
        role_combobox.pack(pady=5, padx=20, fill='x')
        role_combobox.set("user")

        ttk.Label(add_window, text="Phòng ban:").pack(pady=(10, 0))
        department_combobox = ttk.Combobox(add_window, state="readonly")
        department_combobox.pack(pady=5, padx=20, fill='x')
        department_combobox.bind("<<ComboboxSelected>>", load_employees_for_add_window)

        ttk.Label(add_window, text="Nhân viên:").pack(pady=(10, 0))
        employee_combobox = ttk.Combobox(add_window, state="readonly")
        employee_combobox.pack(pady=5, padx=20, fill='x')

        def save_user():
            username = username_entry.get()
            password = password_entry.get()
            role = role_combobox.get()
            employee_name = employee_combobox.get()

            if not all([username, password, role, employee_name]):
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin.", parent=add_window)
                return

            nhanvien_id = employee_map.get(employee_name)
            if not nhanvien_id:
                 messagebox.showerror("Lỗi", "Không tìm thấy ID cho nhân viên được chọn.", parent=add_window)
                 return

            try:
                new_user_id = insert_data("User", {
                    "Username": username,
                    "PasswordHash": password, # Note: Storing plain text passwords is not secure
                    "Role": role,
                    "NhanVienID": nhanvien_id
                })

                if new_user_id:
                    messagebox.showinfo("Thành công", "Thêm người dùng thành công.", parent=add_window)
                    add_window.destroy()
                    self.load_users()
                else:
                    messagebox.showerror("Lỗi", "Không thể thêm người dùng do lỗi không xác định.", parent=add_window)

            except sqlite3.IntegrityError:
                messagebox.showerror("Lỗi", f"Tên đăng nhập '{username}' đã tồn tại hoặc nhân viên đã có tài khoản.", parent=add_window)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm người dùng: {e}", parent=add_window)

        ttk.Button(add_window, text="Lưu", command=save_user, bootstyle=SUCCESS).pack(pady=20)

        load_departments_for_add_window()

    def change_user_password(self):
        selected_user = self.get_selected_user()
        if not selected_user:
            return

        pass_window = ttk.Toplevel(self, "Đổi mật khẩu")
        pass_window.geometry("400x250")
        pass_window.transient(self)
        pass_window.grab_set()

        ttk.Label(pass_window, text=f"Đổi mật khẩu cho {selected_user[1]}", font=("Arial", 12)).pack(pady=(10, 0))

        ttk.Label(pass_window, text="Mật khẩu mới:").pack(pady=(10, 0))
        new_pass_entry = ttk.Entry(pass_window, show="*")
        new_pass_entry.pack(pady=5, padx=20, fill='x')

        ttk.Label(pass_window, text="Nhập lại mật khẩu:").pack(pady=(10, 0))
        confirm_pass_entry = ttk.Entry(pass_window, show="*")
        confirm_pass_entry.pack(pady=5, padx=20, fill='x')

        def save_password():
            new_pass = new_pass_entry.get()
            confirm_pass = confirm_pass_entry.get()

            if not new_pass:
                messagebox.showerror("Lỗi", "Vui lòng nhập mật khẩu mới.", parent=pass_window)
                return
            
            if new_pass != confirm_pass:
                messagebox.showerror("Lỗi", "Mật khẩu nhập lại không khớp.", parent=pass_window)
                return

            try:
                # Note: Storing plain text passwords is not secure
                update_data("User", {"Password": new_pass}, f"UserID = {selected_user[0]}")
                messagebox.showinfo("Thành công", "Đổi mật khẩu thành công.", parent=pass_window)
                pass_window.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đổi mật khẩu: {e}", parent=pass_window)

        ttk.Button(pass_window, text="Lưu", command=save_password, bootstyle=SUCCESS).pack(pady=20)

    def change_user_role(self):
        selected_user = self.get_selected_user()
        if not selected_user:
            return

        role_window = ttk.Toplevel(self, "Đổi vai trò")
        role_window.geometry("400x200")
        role_window.transient(self)
        role_window.grab_set()

        ttk.Label(role_window, text=f"Đổi vai trò cho {selected_user[1]}", font=("Arial", 12)).pack(pady=(10, 0))

        ttk.Label(role_window, text="Vai trò mới:").pack(pady=(10, 0))
        role_combobox = ttk.Combobox(role_window, values=["admin", "user"], state="readonly")
        role_combobox.set(selected_user[2])
        role_combobox.pack(pady=5, padx=20, fill='x')

        def save_role():
            new_role = role_combobox.get()
            if not new_role:
                messagebox.showerror("Lỗi", "Vui lòng chọn vai trò.", parent=role_window)
                return

            try:
                update_data("User", {"Role": new_role}, f"UserID = {selected_user[0]}")
                messagebox.showinfo("Thành công", "Đổi vai trò thành công.", parent=role_window)
                role_window.destroy()
                self.load_users()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đổi vai trò: {e}", parent=role_window)

        ttk.Button(role_window, text="Lưu", command=save_role, bootstyle=SUCCESS).pack(pady=20)