import os
import requests
import json

# 通知したい機種のキーワード
TARGET_MODELS = ["iPhone 16", "iPhone 17"]

def check_apple_store():
    # Appleの整備済製品データのURL
    url = "https://www.apple.com/jp/shop/refurbished/ajax/data/iphone"
    res = requests.get(url)
    data = res.json()
    
    found_items = []
    # 商品リストをループして確認
    for product in data.get('data', {}).get('products', []):
        name = product.get('productName', '')
        # 指定した機種が含まれているかチェック
        if any(model in name for model in TARGET_MODELS):
            price = product.get('price', {}).get('currentPrice', {}).get('amount', '不明')
            found_items.append(f"📱{name}\n価格: {price}円")
            
    return found_items

def send_line(message):
    token = os.environ["LINE_ACCESS_TOKEN"]
    user_id = os.environ["USER_ID"]
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post(url, headers=headers, data=json.dumps(payload))

if __name__ == "__main__":
    items = check_apple_store()
    if items:
        msg = "🔥お目当てのiPhoneが入荷しました！\n\n" + "\n\n".join(items)
        send_line(msg)
