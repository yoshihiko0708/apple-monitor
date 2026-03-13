import os
import requests
import re

# 通知したい機種のキーワード（短くするのがコツです）
TARGET_MODELS = ["15 Pro Max", "16", "17"]

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
        
        found_items = []
        
        # ページを「商品カード」ごとに分割します
        # 整備済製品の各商品は通常 <li> タグなどで区切られています
        products_blocks = content.split('<li class="refurbished-category-grid-no-js">')
        
        for block in products_blocks:
            for model in TARGET_MODELS:
                # 1. そのブロックの中に機種名（15 Proなど）が含まれているか
                # 2. かつ、同じブロック内に「円」という文字があるか（＝価格が表示されている）
                if model in block and "円" in block:
                    # 商品名をきれいに抽出（HTMLタグを除去）
                    name_match = re.search(r'title="([^"]+)"', block)
                    name = name_match.group(1) if name_match else f"iPhone {model}"
                    
                    found_items.append(f"📱{name}")
                    break # 1つのブロックで1つ見つかれば次へ
        
        return list(set(found_items)) # 重複を除去

    except Exception as e:
        print(f"データ取得エラー: {e}")
        return []

# send_line関数は「全員に送る（broadcast）」に書き換えておきます
def send_line(message):
    token = os.environ.get("LINE_ACCESS_TOKEN")
    if not token: return
    
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "messages": [{"type": "text", "text": message}]
    }
    res = requests.post(url, headers=headers, json=payload)
    print(f"LINE送信結果: {res.status_code}")

if __name__ == "__main__":
    items = check_apple_store()
    if items:
        msg = "🔥Apple公式に入荷しました！\n\n" + "\n".join(items) + "\n\n確認はこちら：\nhttps://www.apple.com/jp/shop/refurbished/iphone"
        send_line(msg)
    else:
        print("チェック完了：現在は指定の在庫はありません。")
