import sqlite3

def connect_db():
    """Kết nối đến database và trả về connection object"""
    return sqlite3.connect('boithuong.db')

def execute_query(query, params=None, fetch_one=False):
    """
    Thực thi câu truy vấn SQL
    
    Args:
        query: Câu truy vấn SQL
        params: Các tham số cho câu truy vấn (optional)
        fetch_one: Nếu True chỉ lấy 1 bản ghi, False lấy tất cả
    
    Returns:
        Kết quả truy vấn hoặc None nếu có lỗi
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if fetch_one:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
            
        conn.commit()
        return result
    except Exception as e:
        print(f"Lỗi khi thực thi truy vấn: {e}")
        return None
    finally:
        conn.close()

def insert_data(table, data):
    """
    Chèn dữ liệu vào bảng
    
    Args:
        table: Tên bảng
        data: Dictionary chứa cặp key-value (column: value)
    
    Returns:
        ID của bản ghi mới hoặc None nếu có lỗi
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        cursor.execute(query, tuple(data.values()))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Lỗi khi chèn dữ liệu: {e}")
        return None
    finally:
        conn.close()

def update_data(table, data, condition):
    """
    Cập nhật dữ liệu trong bảng
    
    Args:
        table: Tên bảng
        data: Dictionary chứa cặp key-value (column: value) cần cập nhật
        condition: Điều kiện WHERE (không bao gồm từ khóa WHERE)
    
    Returns:
        Số bản ghi bị ảnh hưởng hoặc None nếu có lỗi
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        
        cursor.execute(query, tuple(data.values()))
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        print(f"Lỗi khi cập nhật dữ liệu: {e}")
        return None
    finally:
        conn.close()