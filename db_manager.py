import sqlite3
import csv
import os

# --- 設定區 ---
DB_NAME = 'inventory.db'
CSV_NAME = 'YN_Inventory.csv'  # 這是你剛才上傳的檔案名稱

def get_conn():
    """建立資料庫連線"""
    return sqlite3.connect(DB_NAME)

def export_to_csv():
    """1. 匯出：將 SQLite 資料庫內容轉存為 CSV (方便用 Numbers 編輯)"""
    if not os.path.exists(DB_NAME):
        print(f"❌ 錯誤：找不到資料庫 {DB_NAME}，請先執行匯入。")
        return

    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM products')
        rows = cursor.fetchall()
        
        # 抓取資料庫中的欄位名稱
        column_names = [description[0] for description in cursor.description]

        with open(CSV_NAME, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(column_names)
            writer.writerows(rows)
            
        print(f"✅ 成功！已匯出至 {CSV_NAME}。")
        print("💡 提示：現在你可以用 Numbers 開啟它，改完後記得選『輸出至 CSV』並覆蓋原檔。")
    except Exception as e:
        print(f"❌ 匯出失敗：{e}")
    finally:
        conn.close()

def import_from_csv():
    """2. 匯入：將 CSV 內容完整覆蓋到 SQLite 資料庫 (包含所有詳細欄位)"""
    if not os.path.exists(CSV_NAME):
        print(f"❌ 錯誤：找不到檔案 {CSV_NAME}，請確認檔案放在 API 資料夾下。")
        return

    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        with open(CSV_NAME, 'r', encoding='utf-8') as f:
            # 使用 DictReader 自動處理標題列
            reader = csv.DictReader(f)
            fields = reader.fieldnames
            
            if not fields:
                print("❌ 錯誤：CSV 檔案內容為空或格式不正確。")
                return

            # 動態建立表格 SQL：根據 CSV 標題自動生成欄位
            # 所有的欄位暫時都設為 TEXT，這在 SQLite 裡處理 CSV 資料最穩定
            columns_sql = ", ".join([f'"{field}" TEXT' for field in fields])
            cursor.execute('DROP TABLE IF EXISTS products')
            cursor.execute(f'CREATE TABLE products ({columns_sql})')

            # 插入資料 SQL
            placeholders = ", ".join(["?" for _ in fields])
            insert_sql = f'INSERT INTO products VALUES ({placeholders})'
            
            count = 0
            for row in reader:
                values = [row[field] for field in fields]
                cursor.execute(insert_sql, values)
                count += 1
        
        conn.commit()
        print(f"✅ 成功！已從 CSV 匯入 {count} 筆商品，共 {len(fields)} 個欄位。")
        print(f"📁 目前欄位包含：{', '.join(fields)}")
        
    except Exception as e:
        print(f"❌ 匯入失敗：{e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("--- YN Select Shop 資料庫管理器 ---")
    print("1. 匯出 (DB -> CSV)：想用 Numbers 改資料時選這個")
    print("2. 匯入 (CSV -> DB)：在 Numbers 改完存檔後選這個")
    
    choice = input("\n請選擇操作序號：")
    
    if choice == '1':
        export_to_csv()
    elif choice == '2':
        import_from_csv()
    else:
        print("無效的選擇，請輸入 1 或 2。")