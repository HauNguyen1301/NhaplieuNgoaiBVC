from database import database_manager as db

with open("database/advanced_query.sql", "r", encoding="utf-8") as f:
    sql = f.read()

try:
    rows = db.fetch_all(sql)
    for r in rows:
        print(r)
except Exception as e:
    print("Error:", e)