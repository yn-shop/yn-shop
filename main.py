import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv

# 載入 .env 裡的隱藏鑰匙
load_dotenv()

app = FastAPI()

# 設定 CORS (讓你的網頁可以跨網域請求 API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 抓取鑰匙並連線到 Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️ 警告：找不到 Supabase 鑰匙，請確認 .env 檔案是否有設定正確！")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 1. 取得所有商品 (給首頁 index.html 使用)
# ==========================================
@app.get("/products")
def get_products():
    # select("*") 會自動把你的 15 個欄位全部抓下來
    response = supabase.table("YN_Inventory").select("*").execute()
    return response.data

# ==========================================
# 2. 取得「單一」商品詳細資料 (給商品頁面 product.html 使用)
# ==========================================
@app.get("/products/{item_id}")
def get_product(item_id: str):
    # 這裡會根據 id，抓出該件衣服專屬的 description, size_details, image_url 等完整資料
    response = supabase.table("YN_Inventory").select("*").eq("id", item_id).execute()
    
    if not response.data:
        return {"error": "找不到商品"}
        
    return response.data[0] # 只回傳該筆商品的完整字典

# ==========================================
# 3. 結帳與扣除庫存 (給結帳按鈕使用)
# ==========================================
@app.post("/checkout/{item_id}")
def checkout(item_id: str):
    # 查詢 Supabase 裡這件衣服目前的庫存
    response = supabase.table("YN_Inventory").select("stock").eq("id", item_id).execute()
    
    if not response.data:
        return {"status": "failed", "message": "找不到該商品"}
        
    current_stock = int(response.data[0]["stock"])
    
    # 判斷是否還有庫存
    if current_stock <= 0:
        return {"status": "failed", "message": "庫存不足，下次請早！"}
        
    # 扣除庫存並寫回 Supabase
    new_stock = current_stock - 1
    supabase.table("YN_Inventory").update({"stock": str(new_stock)}).eq("id", item_id).execute()
    
    return {"status": "success"}