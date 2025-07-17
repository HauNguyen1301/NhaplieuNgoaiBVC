import os
import sys
import re

# --- Kiểm tra và hướng dẫn cài đặt thư viện ---
try:
    from dotenv import load_dotenv
except ImportError:
    print("Lỗi: Thư viện 'python-dotenv' chưa được cài đặt.")
    print("Vui lòng chạy lệnh: pip install python-dotenv")
    sys.exit(1)

try:
    import libsql_client
except ImportError:
    print("Lỗi: Thư viện 'libsql-client' chưa được cài đặt.")
    print("Vui lòng chạy lệnh: pip install libsql-client")
    sys.exit(1)
# ------------------------------------------

SCHEMA_FILE = "database/schema.sql"
DATA_FILE = "database/data.sql"

def execute_sql_from_file(client, file_path, is_schema=False):
    """
    Đọc một tệp SQL, chia nhỏ các câu lệnh INSERT nhiều hàng và thực thi chúng
    một cách tuần tự để dễ dàng gỡ lỗi.
    """
    print(f"\nĐang xử lý tệp: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy tệp {file_path}.")
        return False

    if is_schema:
        content = content.replace('AUTO_INCREMENT', '')
        content = content.replace('DECIMAL(18, 0)', 'INTEGER')

    # Tách các câu lệnh bằng dấu chấm phẩy
    raw_statements = content.split(';')

    final_statements = []
    for stmt in raw_statements:
        stmt = stmt.strip()
        if not stmt:
            continue

        # Xử lý đặc biệt cho các câu lệnh INSERT
        if stmt.upper().startswith("INSERT INTO"):
            # Tìm vị trí của từ khóa VALUES
            values_pos = stmt.upper().find("VALUES")
            if values_pos == -1:
                final_statements.append(stmt)
                continue

            # Tách phần đầu của câu lệnh (INSERT INTO table (cols) VALUES)
            prefix = stmt[:values_pos + len("VALUES")]
            # Tách phần chứa các giá trị
            values_part = stmt[values_pos + len("VALUES"):].strip()

            # Sử dụng regex để tách các bộ giá trị (tuples) một cách an toàn
            # Regex này tìm các cặp dấu ngoặc đơn (...)
            value_tuples = re.findall(r'\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)', values_part)

            for v_tuple in value_tuples:
                # Tạo một câu lệnh INSERT hoàn chỉnh cho mỗi hàng
                single_row_insert = f"{prefix} {v_tuple}"
                final_statements.append(single_row_insert)
        else:
            # Giữ nguyên các câu lệnh khác (CREATE TABLE, etc.)
            final_statements.append(stmt)

    print(f"Thực thi {len(final_statements)} câu lệnh đã xử lý...")
    for i, statement in enumerate(final_statements):
        try:
            # Chỉ lấy kết quả nếu là SELECT, còn lại chỉ thực thi
            if statement.strip().upper().startswith("SELECT"):
                _ = client.execute(statement)
            else:
                client.execute(statement)
        except Exception as e:
            print(f"\n--- LỖI tại câu lệnh số {i + 1} ---")
            print(f"Câu lệnh bị lỗi (tối đa 300 ký tự): {statement[:300]}...")
            print(f"Chi tiết lỗi: {e} (Loại lỗi: {type(e)})")
            return False # Dừng lại khi có lỗi
            
    print(f">>> Thực thi tệp {file_path} thành công.")
    return True


def setup_turso_database():
    """
    Kết nối đến cơ sở dữ liệu Turso, tạo schema và chèn dữ liệu ban đầu.
    """
    load_dotenv()
    url = os.getenv("TURSO_DATABASE_URL")
    auth_token = os.getenv("TURSO_AUTH_TOKEN")

    if not url or not auth_token:
        print("Lỗi: Không tìm thấy TURSO_DATABASE_URL hoặc TURSO_AUTH_TOKEN trong tệp .env.")
        return

    print("Đang kết nối đến cơ sở dữ liệu Turso...")
    https_url = "https://" + url[len("libsql://"):] if url.startswith("libsql://") else url
    print(f"Thực hiện kết nối qua HTTPS: {https_url}")

    client = None
    try:
        client = libsql_client.create_client_sync(url=https_url, auth_token=auth_token)
        print(">>> Kết nối đến Turso thành công.")

        # Xóa bảng cũ
        print("\nĐang kiểm tra và xóa các bảng cũ...")
        rs = client.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in rs.rows if not row[0].startswith(('sqlite_', '_litestream'))]
        if tables:
            # Tạm thởi tắt kiểm tra khóa ngoại để tránh lỗi khi xóa bảng
            try:
                client.execute("PRAGMA foreign_keys = OFF;")
            except Exception:
                pass
            drop_stmts = [f"DROP TABLE IF EXISTS {tbl};" for tbl in tables]
            print(f"Tìm thấy {len(drop_stmts)} bảng để xóa: {', '.join(tables)}")
            client.batch(drop_stmts)
            print(">>> Đã xóa thành công các bảng cũ.")
            try:
                client.execute("PRAGMA foreign_keys = ON;")
            except Exception:
                pass
        else:
            print(">>> Không có bảng cũ nào cần xóa.")

        # Thực thi schema và data
        if not execute_sql_from_file(client, SCHEMA_FILE, is_schema=True):
            return # Dừng nếu có lỗi
        if not execute_sql_from_file(client, DATA_FILE):
            return # Dừng nếu có lỗi

        print("\n>>> Thiết lập cơ sở dữ liệu Turso hoàn tất.")

    except Exception as e:
        print(f"\nĐã xảy ra lỗi nghiêm trọng: {e}")
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    setup_turso_database()
