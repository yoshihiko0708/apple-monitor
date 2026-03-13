import os
import requests
import json

# 通知したい機種のキーワード
TARGET_MODELS = ["15 Pro Max", "16", "17"]

def check_apple_store():
    # AppleのデータURL
    url = "https://www.apple.com/jp/shop/refurbished/ajax/data/iphone"
    
    # 【究極の対策】ブラウザのふりをする情報をさらに詳しく追加
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        "Referer": "https://www.apple.com/jp/shop/refurbished/iphone",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        # タイムアウト（待ち時間）も設定して、より自然にアクセス
        res = requests.get(url, headers=headers, timeout=10)
        
        # もしアクセス拒否（403等）されたらここでエラーを表示させる
        if res.status_code != 200:
            print(f"Apple側でブロックされました。ステータスコード: {res.status_code}")
            return []
            
        data = res.json()
    except Exception as e:
        print(f"データ取得エラー: {e}")
        # エラーの中身をもっと詳しく見るために追加
        if 'res' in locals():
            print(f"取得した生データの一部: {res.text[:100]}") 
        return []
    
    found_items = []
    products = data.get('data', {}).get('products', [])
    for product in products:
        name = product.get('productName', '')
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
        print("現在は対象機種の在庫がありません。（データ取得は成功しています）")
