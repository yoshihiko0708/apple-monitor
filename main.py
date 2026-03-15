import os
import requests
import re

# キーワード（完全一致を狙うため、iPhoneも含めます）
TARGET_MODELS = ["iPhone 15 Pro", "iPhone 15 Pro Max", "iPhone 16", "iPhone 17"]

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
        
        # 【最重要】サイドバーとフッターを物理的に切り捨てます
        # 商品が並ぶ「grid」というキーワードで分割し、商品エリアだけを抽出
        if 'class="refurbished-category-grid' not in content:
            print("商品グリッドが見つかりません。在庫がゼロの可能性があります。")
            return []
            
        # 商品エリア（右側）の開始位置を特定
        product_area = content.split('class="refurbished-category-grid')[1]
        # 商品エリアの終了位置（次の大きなセクションまで）で切る
        product_area = product_area.split('</section>')[0]

        # 商品エリアを「1つの商品カード」ごとにバラバラに分解します
        # 整備済製品は必ずこのクラス名の中に情報がまとまっています
        tiles = product_area.split('class="refurbished-category-grid-item')
        
        found_items = []
        
        for tile in tiles[1:]: # 最初の欠片は無視
            for model in TARGET_MODELS:
                # 判定条件：
                # 1. その「商品カード」の中に機種名が含まれている
                # 2. かつ、同じ「カード内」に価格（〇〇円）が含まれている
                if model in tile and "円" in tile:
                    # 商品名を抽出（data-related-product-name 属性が最も正確です）
                    name_match = re.search(r'data-related-product-name="([^"]+)"', tile)
                    if name_match:
                        full_name = name_match.group(1)
                        found_items.append(f"📱{full_name}")
                        break
        
        return list(set(found_items))

    except Exception as e:
        print(f"解析エラー: {e}")
        return []

def send_line(message):
    token = os.environ.get("LINE_ACCESS_TOKEN")
    if not token: return
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    payload = {"messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    items = check_apple_store()
    if items:
        msg = "🔥【本物の在庫】Apple公式に入荷しました！\n\n" + "\n".join(items) + "\n\n今すぐ確認：\nhttps://www.apple.com/jp/shop/refurbished/iphone"
        send_line(msg)
        print(f"検知成功: {items}")
    else:
        print("チェック完了：現在は条件に一致する『購入可能な商品』はありません。")
