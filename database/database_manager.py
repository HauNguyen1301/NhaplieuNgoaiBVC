import sqlite3
import os

# Lấy đường dẫn tuyệt đối đến thư mục chứa file script này (database/)
_script_dir = os.path.dirname(os.path.abspath(__file__))
# Lấy đường dẫn tuyệt đối đến thư mục gốc của dự án
_project_root = os.path.dirname(_script_dir)
# Tạo đường dẫn tuyệt đối đến file cơ sở dữ liệu
DB_PATH = os.path.join(_project_root, 'database', 'boithuong.db')

def get_db_connection():
    """Tạo và trả về một kết nối đến cơ sở dữ liệu SQLite."""
    return sqlite3.connect(DB_PATH)

def fetch_all(query, params=()):
    """Thực thi một truy vấn SELECT và trả về tất cả các hàng kết quả."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Lỗi cơ sở dữ liệu: {e}")
        return []
    finally:
        if conn:
            conn.close()

def fetch_one(query, params=()):
    """Thực thi một truy vấn SELECT và trả về một hàng kết quả."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Lỗi cơ sở dữ liệu: {e}")
        return None
    finally:
        if conn:
            conn.close()

def execute_query(query, params=()):
    """Thực thi một truy vấn INSERT, UPDATE, hoặc DELETE."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Lỗi cơ sở dữ liệu khi thực thi: {e}")
        return False
    finally:
        if conn:
            conn.close()

def fetch_all_as_dict(query, params=()):
    """Thực thi một truy vấn SELECT và trả về tất cả các hàng kết quả dưới dạng list of dicts."""
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row # Trả về kết quả dạng dictionary
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        # Chuyển đổi các đối tượng sqlite3.Row thành dicts
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"Lỗi cơ sở dữ liệu: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_nhan_vien_id_from_user_id(user_id):
    """Lấy NhanVienID từ UserID."""
    result = fetch_one("SELECT NhanVienID FROM User WHERE UserID = ?", (user_id,))
    return result[0] if result else None

def get_ho_so_details_for_display(ho_so_id):
    sql = """
        SELECT 
            hs.SoHoSo, hs.NguoiDuocBaoHiem, hs.KhachHang, hs.SoTheBaoHiem, hs.SoHopDongBaoHiem,
            hs.HLBH_tu, hs.HLBH_den, hs.NgayNhanHoSo, hs.NgayRuiRo,
            hs.SoTienYeuCau, hs.SoTienBoiThuong, hs.NgayBoiThuong, hs.MoTaNguyenNhan, hs.HauQua, hs.GiaiQuyet,
            sp.TenSanPham, cty.TenCTTV AS TenCongTy, lb.TenLoaiBenh, tt.TenTinhTrang,
            cb.HoTen AS CanBoBoiThuong,
            nguoi_nhap.HoTen AS NguoiNhap,
            hs.time_create, hs.time_update
        FROM HoSoBoiThuong hs
        LEFT JOIN SanPham sp ON hs.SanPhamID = sp.SanPhamID
        LEFT JOIN CTTV cty ON hs.CTTVID = cty.CTTVID
        LEFT JOIN LoaiBenh lb ON hs.LoaiBenhID = lb.LoaiBenhID
        LEFT JOIN TinhTrangHoSo tt ON hs.TinhTrangID = tt.TinhTrangID
        LEFT JOIN NhanVien cb ON hs.CanBoBoiThuongID = cb.NhanVienID
        LEFT JOIN User u_creator ON hs.created_by = u_creator.UserID
        LEFT JOIN NhanVien nguoi_nhap ON u_creator.NhanVienID = nguoi_nhap.NhanVienID
        WHERE hs.ID = ?
    """
    results = fetch_all_as_dict(sql, (ho_so_id,))
    return results[0] if results else None

def get_ban_cap_dons():
    """Lấy danh sách các ban cấp đơn duy nhất từ bảng SanPham."""
    return fetch_all("SELECT DISTINCT BanCapDon FROM SanPham WHERE BanCapDon IS NOT NULL ORDER BY BanCapDon")

def get_cttvs():
    """Lấy danh sách các công ty thành viên."""
    return fetch_all("SELECT TenCTTV FROM CTTV ORDER BY TenCTTV")

def get_phong_bans():
    return fetch_all("SELECT DISTINCT HR_PhongBan FROM NhanVien WHERE HR_PhongBan IS NOT NULL ORDER BY HR_PhongBan")

def get_can_bos_by_phong_ban(phong_ban):
    return fetch_all("SELECT HoTen FROM NhanVien WHERE HR_PhongBan = ? ORDER BY HoTen", (phong_ban,))

def get_loai_benhs():
    return fetch_all("SELECT TenLoaiBenh FROM LoaiBenh ORDER BY TenLoaiBenh")

def get_tinh_trang_ho_so():
    return fetch_all("SELECT TenTinhTrang FROM TinhTrangHoSo ORDER BY TinhTrangID")

def get_all_tinh_trang():
    """Lấy danh sách tất cả tình trạng (ID và Tên)."""
    return fetch_all("SELECT TinhTrangID, TenTinhTrang FROM TinhTrangHoSo ORDER BY TinhTrangID")

def get_all_nhan_vien():
    """Lấy danh sách tất cả nhân viên (ID và Tên)."""
    return fetch_all("SELECT NhanVienID, HoTen FROM NhanVien ORDER BY HoTen")

def get_san_phams_by_ban(ban_cap_don):
    return fetch_all("SELECT TenSanPham FROM SanPham WHERE BanCapDon = ? ORDER BY TenSanPham", (ban_cap_don,))

def get_san_phams():
    return fetch_all("SELECT TenSanPham FROM SanPham ORDER BY TenSanPham")

def get_name_by_id(table, name_column, id_column, item_id):
    """
    Lấy tên/giá trị từ một bảng dựa vào ID.
    """
    if item_id is None:
        return ""
    query = f'SELECT {name_column} FROM {table} WHERE {id_column} = ?'
    result = fetch_one(query, (item_id,))
    return result[0] if result else ""

def get_ban_name_by_san_pham_id(san_pham_id):
    """Lấy tên Ban Cấp Đơn từ SanPhamID."""
    if san_pham_id is None: 
        return ""
    query = 'SELECT BanCapDon FROM SanPham WHERE SanPhamID = ?'
    result = fetch_one(query, (san_pham_id,))
    return result[0] if result else ""

def get_phong_ban_by_nhan_vien_id(nhan_vien_id):
    """Lấy tên Phòng ban từ NhanVienID."""
    if nhan_vien_id is None: 
        return ""
    query = 'SELECT HR_PhongBan FROM NhanVien WHERE NhanVienID = ?'
    result = fetch_one(query, (nhan_vien_id,))
    return result[0] if result else ""

def get_id_by_name(table, id_column, name_column, name):
    result = fetch_one(f'SELECT {id_column} FROM {table} WHERE {name_column} = ?', (name,))
    return result[0] if result else None

def insert_gyctt(data):
    sql = """
        INSERT INTO HoSoBoiThuong (
            SoHoSo, NguoiDuocBaoHiem, KhachHang, HLBH_tu, HLBH_den, 
            NgayRuiRo, NgayNhanHoSo, SoTienYeuCau, SoTienBoiThuong, TinhTrangID, LoaiBenhID, 
            MoTaNguyenNhan, CTTVID, SanPhamID, CanBoBoiThuongID, SoTheBaoHiem, SoHopDongBaoHiem, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    return execute_query(sql, data)

def get_ho_so_for_statistic(status_ids=None, phong_ban=None, user_id_for_cbbt=None):
    """
    Lấy danh sách hồ sơ cho trang thống kê.
    - status_ids: một list hoặc tuple các TinhTrangID để lọc. Nếu None, lấy tất cả.
    - phong_ban: tên phòng ban để lọc. Nếu None, không lọc theo phòng ban.
    """
    base_query = """
        SELECT 
            hs.ID, 
            hs.SoHoSo, 
            hs.NguoiDuocBaoHiem, 
            sp.TenSanPham, 
            hs.SoTienYeuCau, 
            tt.TenTinhTrang, 
            hs.NgayNhanHoSo,
            cb.HoTen AS CanBoBoiThuong,
            nguoi_nhap.HoTen AS NguoiNhap
        FROM HoSoBoiThuong hs
        LEFT JOIN SanPham sp ON hs.SanPhamID = sp.SanPhamID
        LEFT JOIN NhanVien cb ON hs.CanBoBoiThuongID = cb.NhanVienID
        LEFT JOIN TinhTrangHoSo tt ON hs.TinhTrangID = tt.TinhTrangID
        LEFT JOIN User u ON hs.created_by = u.UserID
        LEFT JOIN NhanVien nguoi_nhap ON u.NhanVienID = nguoi_nhap.NhanVienID
    """
    where_clauses = []
    params = []

    if status_ids:
        placeholders = ','.join(['?'] * len(status_ids))
        where_clauses.append(f"hs.TinhTrangID IN ({placeholders})")
        params.extend(status_ids)

    if phong_ban:
        where_clauses.append("cb.HR_PhongBan = ?")
        params.append(phong_ban)
    
    if user_id_for_cbbt:
        # Lấy NhanVienID từ UserID
        nhan_vien_id = get_nhan_vien_id_from_user_id(user_id_for_cbbt)
        if nhan_vien_id:
            where_clauses.append("(hs.created_by = ? OR hs.CanBoBoiThuongID = ?)")
            params.extend([user_id_for_cbbt, nhan_vien_id])

    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)
    
    base_query += " ORDER BY hs.time_create DESC"

    return fetch_all(base_query, params)

def search_ho_so(so_ho_so=None, ten_ndbh=None):
    """
    Tìm kiếm hồ sơ dựa trên Số hồ sơ và/hoặc Tên Người được bảo hiểm.
    Sử dụng LIKE để tìm kiếm gần đúng.
    """
    query = """
        SELECT 
            hs.ID, -- Lấy ID để sử dụng sau này
            hs.SoHoSo, 
            hs.NguoiDuocBaoHiem,
            sp.MaSanPham,
            tths.TenTinhTrang
        FROM HoSoBoiThuong hs
        LEFT JOIN SanPham sp ON hs.SanPhamID = sp.SanPhamID
        LEFT JOIN TinhTrangHoSo tths ON hs.TinhTrangID = tths.TinhTrangID
    """
    conditions = ["hs.TinhTrangID != 5"]
    params = []

    if so_ho_so:
        conditions.append("hs.SoHoSo LIKE ?")
        params.append(f"%{so_ho_so}%")
    
    if ten_ndbh:
        conditions.append("hs.NguoiDuocBaoHiem LIKE ?")
        params.append(f"%{ten_ndbh}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY hs.time_create DESC"
        return fetch_all(query, tuple(params))
    else:
        return []

def get_ho_so_by_id(hs_id):
    """
    Lấy tất cả thông tin chi tiết của một hồ sơ bồi thường bằng ID.
    """
    query = """SELECT 
        ID, SoHoSo, NguoiDuocBaoHiem, KhachHang, HLBH_tu, HLBH_den,
        NgayRuiRo, NgayNhanHoSo, SoTienYeuCau, SoTienBoiThuong, TinhTrangID, LoaiBenhID, 
        MoTaNguyenNhan, CTTVID, SanPhamID, CanBoBoiThuongID, SoTheBaoHiem, SoHopDongBaoHiem, time_create,
        NgayBoiThuong, HauQua, GiaiQuyet, NguoiDuyetID
        FROM HoSoBoiThuong WHERE ID = ?"""
    return fetch_one(query, (hs_id,))

def update_ho_so(hs_id, data_tuple):
    """
    Cập nhật thông tin hồ sơ bồi thường dựa trên ID.
    data_tuple phải chứa các giá trị theo đúng thứ tự các cột (trừ SoHoSo và ID).
    """
    query = """UPDATE HoSoBoiThuong SET
        NguoiDuocBaoHiem = ?, KhachHang = ?, HLBH_tu = ?, HLBH_den = ?,
        NgayRuiRo = ?, NgayNhanHoSo = ?, SoTienYeuCau = ?, SoTienBoiThuong = ?, TinhTrangID = ?, LoaiBenhID = ?,
        MoTaNguyenNhan = ?, CTTVID = ?, SanPhamID = ?, CanBoBoiThuongID = ?, SoTheBaoHiem = ?, SoHopDongBaoHiem = ?
        WHERE ID = ?
    """
    # Thêm hs_id vào cuối tuple dữ liệu cho điều kiện WHERE
    full_data_tuple = data_tuple + (hs_id,)
    return execute_query(query, full_data_tuple)

def update_to_trinh(hs_id, data_tuple):
    """
    Cập nhật thông tin tờ trình bồi thường.
    """
    query = """UPDATE HoSoBoiThuong SET
        NgayBoiThuong = ?, HauQua = ?, GiaiQuyet = ?, SoTienBoiThuong = ?,
        NguoiDuyetID = ?, TinhTrangID = ?, CanBoBoiThuongID = ?, time_update = ?
        WHERE ID = ?
    """
    full_data_tuple = data_tuple + (hs_id,)
    return execute_query(query, full_data_tuple)



