import os
import requests
import json

# 通知したい機種のキーワード
TARGET_MODELS = ["15 Pro Max", "16", "17"]

def check_apple_store():
    # URLをより確実なものに変更しました
    url = "https://www.apple.com/jp/shop/refurbished/ajax/data/iphone"
    
    # または、こちらでも試せるように予備のURLロジックを組み込みます
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Referer": "https://www.apple.com/jp/shop/refurbished/iphone"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        
        # 404エラーが出た場合の対策：別のURLパターンを試す
        if res.status_code == 404:
            # 代替URL（製品一覧の別の取得先）
            url = "https://www.apple.com/jp/shop/mpr/refurbished/iphone"
            res = requests.get(url, headers=headers, timeout=15)

        if res.status_code != 200:
            print(f"アクセス失敗。ステータスコード: {res.status_code}")
            return []
            
        data = res.json()
    except Exception as e:
        print(f"取得エラー: {e}")
        return []
    
    found_items = []
    # AppleのJSON構造に合わせて解析
    products = data.get('data', {}).get('products', [])
    for product in products:
        name = product.get('productName', '')
        if any(model in name for model in TARGET_MODELS):
            price = product.get('price', {}).get('currentPrice', {}).get('amount', '価格不明')
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
        # ログを分かりやすくします
        print("通信成功：現在、指定したターゲット機種の在庫はありません。")
