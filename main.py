import os
import requests
import re

# キーワード
TARGET_MODELS = ["iPhone 16", "iPhone 17"]

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
        
        # 【最重要】サイドバーのメニュー部分をまるごとカットします
        # 商品が並び始める「grid」よりも前の部分は検索対象から外します
        if 'class="refurbished-category-grid"' in content:
            main_content = content.split('class="refurbished-category-grid"')[1]
        else:
            main_content = content

        # 商品カードごとに分割
        products_blocks = main_content.split('class="refurbished-category-grid-item')
        
        found_items = []
        
        for block in products_blocks:
            for model in TARGET_MODELS:
                # 1. 機種名が含まれている
                # 2. かつ、「お届け」や「受取」などの購入可能ワードがある
                # 3. かつ、「円」という価格表示がある
                if model in block and ("お届け" in block or "受取" in block) and "円" in block:
                    
                    # より正確な商品名を取得
                    name_match = re.search(r'data-related-product-name="([^"]+)"', block)
                    if not name_match:
                        name_match = re.search(r'title="([^"]+)"', block)
                    
                    name = name_match.group(1) if name_match else f"iPhone {model}"
                    
                    # ゴミデータ（サイドバーの名残りなど）を拾わないためのガード
                    if len(name) < 50: # あまりに長い名前は除外
                        found_items.append(name)
                    break
        
        return list(set(found_items))

    except Exception as e:
        print(f"データ取得エラー: {e}")
        return []

# send_line, main の部分は前回と同様です
