SELECT
    hs.SoHoSo,
    hs.NguoiDuocBaoHiem,
    sp.MaSanPham,
    hs.SoTienYeuCau,
    hs.SoTienBoiThuong,
    tths.TenTinhTrang,
    hs.NgayNhanHoSo,
    hs.NgayBoiThuong,
    cb.HoTen
FROM HoSoBoiThuong hs
LEFT JOIN SanPham sp         ON hs.SanPhamID       = sp.SanPhamID
LEFT JOIN TinhTrangHoSo tths ON hs.TinhTrangID     = tths.TinhTrangID
LEFT JOIN NhanVien cb        ON hs.CanBoBoiThuongID = cb.NhanVienID
LEFT JOIN NhanVien pb ON cb.NhanVienID = pb.NhanVienID
ORDER BY hs.time_create DESC;