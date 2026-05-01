import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 跨域設定 (讓你的網頁能存取)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 建立資料庫連線的工具
def get_db():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/products")
def get_products():
    conn = get_db()
    cursor = conn.cursor()
    # 這裡會從 SQLite 檔案讀取，而不是從程式碼讀取
    cursor.execute('SELECT * FROM products')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/checkout/{item_id}")
def checkout(item_id: str):
    conn = get_db()
    cursor = conn.cursor()
    # 這是真正的扣庫存邏輯
    cursor.execute('UPDATE products SET stock = stock - 1 WHERE id = ? AND stock > 0', (item_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return {"status": "success" if success else "out_of_stock"}