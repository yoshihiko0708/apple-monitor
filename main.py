import os
import requests
import json

# 通知したい機種のキーワード
TARGET_MODELS = ["iPhone 15 Pro Max", "iPhone 16", "iPhone 17"]

def check_apple_store():
    # Appleのデータ取得用URL
    url = "https://www.apple.com/jp/shop/refurbished/ajax/data/iphone"
    
    # 【重要】ブラウザからのアクセスに見せかけるための設定
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status() # エラーがあればここで止める
        data = res.json()
    except Exception as e:
        print(f"データ取得エラー: {e}")
        return []
    
    found_items = []
    # 商品リストをループして確認
    products = data.get('data', {}).get('products', [])
    for product in products:
        name = product.get('productName', '')
        # 指定した機種が含まれているかチェック
        if any(model in name for model in TARGET_MODELS):
            # 価格情報を取得（少し複雑な構造なので丁寧に抽出）
            price_data = product.get('price', {}).get('currentPrice', {})
            price = price_data.get('amount', '価格不明')
            found_items.append(f"📱{name}\n価格: {price}円")
            
    return found_items

def send_line(message):
    token = os.environ.get("LINE_ACCESS_TOKEN")
    user_id = os.environ.get("USER_ID")
    
    if not token or not user_id:
        print("LINE設定（Secrets）が見つかりません。")
        return

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
        msg = "🔥Apple整備済製品が入荷しました！\n\n" + "\n\n".join(items)
        send_line(msg)
    else:
        print("対象の在庫はありませんでした。")
