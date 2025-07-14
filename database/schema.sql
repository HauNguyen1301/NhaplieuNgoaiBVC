-- Bảng tham chiếu cho các Đơn vị cấp đơn (trước đây là CongTy)
CREATE TABLE CTTV (
    CTTVID INT PRIMARY KEY AUTO_INCREMENT,
    TenCTTV VARCHAR(255) UNIQUE NOT NULL
);

-- Bảng tham chiếu cho các Sản phẩm (không đổi)
CREATE TABLE SanPham (
    SanPhamID INT PRIMARY KEY AUTO_INCREMENT,
    MaSanPham VARCHAR(50) UNIQUE,
    TenSanPham VARCHAR(50) UNIQUE NOT NULL,
    BanCapDon VARCHAR(50) NOT NULL
);

-- Bảng tham chiếu cho Nhân viên (không đổi)
CREATE TABLE NhanVien (
    NhanVienID INT PRIMARY KEY AUTO_INCREMENT,
    HoTen VARCHAR(255) UNIQUE NOT NULL,
    HR_PhongBan VARCHAR(255)
);

-- Bảng mới: Nhóm Nguyên nhân chính
CREATE TABLE NguyenNhan (
    NguyenNhanID INT PRIMARY KEY AUTO_INCREMENT,
    TenNguyenNhan VARCHAR(255) UNIQUE NOT NULL
);

-- Bảng mới: Loại bệnh/Quyền lợi chi tiết
CREATE TABLE LoaiBenh (
    LoaiBenhID INT PRIMARY KEY AUTO_INCREMENT,
    MaLoaiBenh VARCHAR(20) UNIQUE, -- Mã như '1.1', '2.1'
    TenLoaiBenh VARCHAR(255) NOT NULL,
    NguyenNhanID INT, -- Khóa ngoại liên kết với bảng NguyenNhan
    CONSTRAINT fk_nguyennhan FOREIGN KEY (NguyenNhanID) REFERENCES NguyenNhan(NguyenNhanID)
);

-- Bảng mới: Tình Trạng Hồ Sơ
CREATE TABLE TinhTrangHoSo (
    TinhTrangID INT PRIMARY KEY AUTO_INCREMENT,
    TenTinhTrang VARCHAR(100) UNIQUE NOT NULL
);

-- Bảng chính HoSoBoiThuong (đã cập nhật)
CREATE TABLE HoSoBoiThuong (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    SoHoSo VARCHAR(100) UNIQUE NOT NULL,
    SoTheBaoHiem VARCHAR(255) NOT NULL ,
    SoHopDongBaoHiem VARCHAR(255) NOT NULL ,
    NguoiDuocBaoHiem VARCHAR(255),
    KhachHang VARCHAR(255),
    HLBH_tu DATE,
    HLBH_den DATE,
    NgayRuiRo DATE,
    NgayNhanHoSo DATE,
    NgayBoiThuong DATE,
    SoTienYeuCau DECIMAL(18, 0) DEFAULT 0,
    SoTienBoiThuong DECIMAL(18, 0) DEFAULT 0,
    TinhTrangID INT,
    LoaiBenhID INT,
    MoTaNguyenNhan TEXT,
    HauQua TEXT,
    GiaiQuyet TEXT,

    -- Các cột khóa ngoại (Foreign Keys)
    CTTVID INT,
    SanPhamID INT,
    CanBoBoiThuongID INT,
    NguoiDuyetID INT,
    time_create TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    time_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Thiết lập mối quan hệ giữa các bảng
    CONSTRAINT fk_CTTV FOREIGN KEY (CTTVID) REFERENCES CTTV(CTTVID),
    CONSTRAINT fk_sanpham FOREIGN KEY (SanPhamID) REFERENCES SanPham(SanPhamID),
    CONSTRAINT fk_loaibenh FOREIGN KEY (LoaiBenhID) REFERENCES LoaiBenh(LoaiBenhID),
    CONSTRAINT fk_canbobt FOREIGN KEY (CanBoBoiThuongID) REFERENCES NhanVien(NhanVienID),
    CONSTRAINT fk_nguoiduyet FOREIGN KEY (NguoiDuyetID) REFERENCES NhanVien(NhanVienID),
    CONSTRAINT fk_tinhtrang FOREIGN KEY (TinhTrangID) REFERENCES TinhTrangHoSo(TinhTrangID)
);

-- Tạo các chỉ mục (INDEX) cho bảng HoSoBoiThuong
CREATE INDEX idx_tinh_trang ON HoSoBoiThuong (TinhTrangID);
CREATE INDEX idx_ngay_nhan_hs ON HoSoBoiThuong (NgayNhanHoSo);
CREATE INDEX idx_ngay_boi_thuong ON HoSoBoiThuong (NgayBoiThuong);
CREATE INDEX idx_can_bo_bt ON HoSoBoiThuong (CanBoBoiThuongID);

-- Bảng User để quản lý đăng nhập
CREATE TABLE User (
    UserID INTEGER PRIMARY KEY,
    Username VARCHAR(255) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Role VARCHAR(50) NOT NULL, -- e.g., 'admin', 'user'
    NhanVienID INT UNIQUE, -- Mỗi nhân viên chỉ có 1 tài khoản
    CONSTRAINT fk_user_nhanvien FOREIGN KEY (NhanVienID) REFERENCES NhanVien(NhanVienID)
);

-- Bảng log theo dõi thay đổi
CREATE TABLE system_audit_log (
    id INTEGER PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    operation_type VARCHAR(50) NOT NULL, -- e.g., 'INSERT', 'UPDATE', 'DELETE'
    record_id INTEGER,
    old_values TEXT,
    new_values TEXT,
    changed_by INTEGER,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (changed_by) REFERENCES User(UserID)
);