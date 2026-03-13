import os
import requests
import json

# 通知したい機種のキーワード（ここに入っている文字が含まれれば通知されます）
TARGET_MODELS = ["15 Pro Max", "16", "17"]

def check_apple_store():
    url = "https://www.apple.com/jp/shop/refurbished/ajax/data/iphone"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"データ取得エラー: {e}")
        return []
    
    found_items = []
    products = data.get('data', {}).get('products', [])
    for product in products:
        name = product.get('productName', '')
        # 指定したキーワードのいずれかが名前に入っているかチェック
        if any(model in name for model in TARGET_MODELS):
            price_data = product.get('price', {}).get('currentPrice', {})
            price = price_data.get('amount', '価格不明')
            found_items.append(f"📱{name}\n価格: {price}円")
            
    return found_items

def send_line(message):
    token = os.environ.get("LINE_ACCESS_TOKEN")
    user_id = os.environ.get("USER_ID")
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    items = check_apple_store()
    if items:
        msg = "🔥お目当てのiPhoneが入荷しました！\n\n" + "\n\n".join(items)
        send_line(msg)
    else:
        print("現在は対象機種の在庫がありません。")
