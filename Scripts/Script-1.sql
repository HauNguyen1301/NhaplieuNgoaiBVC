/*
  TẬP LỆNH DI CHUYỂN BẢNG HoSoBoiThuong
  Mục đích: Cập nhật cấu trúc bảng HoSoBoiThuong để có cột ID tự động tăng
            và thêm các cột mới, trong khi vẫn giữ lại dữ liệu hiện có.
  Các bước:
  1. Đổi tên bảng cũ.
  2. Tạo bảng mới với cấu trúc chuẩn và ID tự động tăng.
  3. Sao chép dữ liệu từ bảng cũ sang bảng mới.
  4. Xóa bảng cũ.
  5. Tạo lại các chỉ mục (index) cho bảng mới.
*/

-- Bắt đầu một transaction để đảm bảo an toàn dữ liệu
BEGIN TRANSACTION;

-- Bước 1: Đổi tên bảng hiện tại
ALTER TABLE HoSoBoiThuong RENAME TO HoSoBoiThuong_old;

-- Bước 2: Tạo lại bảng với cấu trúc chuẩn và ID tự động tăng
CREATE TABLE HoSoBoiThuong (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    SoHoSo VARCHAR(100) UNIQUE NOT NULL,
    SoTheBaoHiem VARCHAR(255) NOT NULL,
    SoHopDongBaoHiem VARCHAR(255) NOT NULL,
    NguoiDuocBaoHiem VARCHAR(255),
    KhachHang VARCHAR(255),
    HLBH_tu DATE,
    HLBH_den DATE,
    NgayRuiRo DATE,
    NgayNhanHoSo DATE,
    NgayBoiThuong DATE,
    SoTienYeuCau INTEGER DEFAULT 0,
    SoTienBoiThuong INTEGER DEFAULT 0,
    TinhTrangID INT,
    LoaiBenhID INT,
    MoTaNguyenNhan TEXT,
    HauQua TEXT,
    GiaiQuyet TEXT,
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

-- Bước 3: Sao chép dữ liệu từ bảng cũ sang bảng mới
-- Lưu ý: Danh sách cột ở đây phải khớp với bảng cũ của bạn.
-- Giả sử bảng cũ có các cột như trong ảnh bạn gửi.
INSERT INTO HoSoBoiThuong (
    SoHoSo, SoTheBaoHiem, SoHopDongBaoHiem, NguoiDuocBaoHiem, KhachHang,
    HLBH_tu, HLBH_den, NgayRuiRo, NgayNhanHoSo, NgayBoiThuong,
    SoTienYeuCau, SoTienBoiThuong, TinhTrangID, LoaiBenhID, MoTaNguyenNhan
)
SELECT
    SoHoSo, SoTheBaoHiem, SoHopDongBaoHiem, NguoiDuocBaoHiem, KhachHang,
    HLBH_tu, HLBH_den, NgayRuiRo, NgayNhanHoSo, NgayBoiThuong,
    SoTienYeuCau, SoTienBoiThuong, TinhTrangID, LoaiBenhID, MoTaNguyenNhan
FROM HoSoBoiThuong_old;

-- Bước 4: Xóa bảng cũ đi
DROP TABLE HoSoBoiThuong_old;

-- Bước 5: Tạo lại các chỉ mục (Indexes) để tăng tốc độ truy vấn cho bảng mới
CREATE INDEX idx_tinh_trang ON HoSoBoiThuong (TinhTrangID);
CREATE INDEX idx_ngay_nhan_hs ON HoSoBoiThuong (NgayNhanHoSo);
CREATE INDEX idx_ngay_boi_thuong ON HoSoBoiThuong (NgayBoiThuong);
CREATE INDEX idx_can_bo_bt ON HoSoBoiThuong (CanBoBoiThuongID);

-- Kết thúc transaction và lưu các thay đổi
COMMIT;

