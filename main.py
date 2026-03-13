import os
import requests
import re # 文字検索を強化するためのライブラリ

TARGET_MODELS = ["iPhone 15 Pro Max", "iPhone 16", "iPhone 17"]

def check_apple_store():
    url = "https://www.apple.com/jp/shop/refurbished/iphone"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ja-JP,ja;q=0.9",
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        content = res.text
        
        # ページを「商品ごと」のブロックに分割して解析する（簡易的な方法）
        # 各商品は "refurbished-category-grid-no-js" などの塊の中にあります
        # ここでは、より確実に「価格（円）」とセットで名前が出ているかを確認します
        
        found_items = []
        
        for model in TARGET_MODELS:
            # 正規表現を使って「機種名」のあとに「価格（数字 + 円）」が続くパターンを探す
            # これにより、ただ名前が載っているだけのリンクや説明文を無視できます
            pattern = rf"{model}.*?[\d,]+円" 
            if re.search(pattern, content, re.DOTALL):
                found_items.append(f"📱{model} (在庫あり)")
        
        return found_items

    except Exception as e:
        print(f"データ取得エラー: {e}")
        return []

# --- 以下の send_line と main 部分は前回と同じ ---
