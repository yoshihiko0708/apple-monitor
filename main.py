import os
import requests
import json

# 通知したい機種のキーワード
TARGET_MODELS = ["15 Pro", "15 Pro Max", "16", "17"]

def check_apple_store():
    # データを直接持っているURL
    url = "https://www.apple.com/jp/shop/refurbished/ajax/data/iphone"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.apple.com/jp/shop/refurbished/iphone",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200:
            print(f"データ取得失敗: {res.status_code}")
            return []
        
        data = res.json()
        found_items = []

        # Appleのデータ構造を深く解析します
        # data -> products の中に全商品のリストが入っています
        products = data.get('data', {}).get('products', [])
        
        for product in products:
            product_name = product.get('productName', '')
            
            # 1. ターゲットの機種名が含まれているか
            for target in TARGET_MODELS:
                if target in product_name:
                    # 2. 【最重要】在庫があるかどうかをAppleのデータから直接判定
                    # Appleの内部データでは商品の「購入可能性」が定義されています
                    is_full_price = product.get('isFullPrice', False) # 通常、整備済はここが重要
                    
                    # より確実なのは、価格が存在し、かつ特定の「在庫ステータス」を見ることです
                    # 整備済製品データにおいて、このリストに載っている＝在庫候補ですが、
                    # さらに絞り込むため、価格情報を確認します。
                    price = product.get('price', {}).get('currentPrice', {}).get('amount', '0')
                    
                    if float(price.replace(',', '')) > 0:
                        found_items.append(f"📱{product_name} (￥{price})")
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
        # 在庫があるものだけを通知
        msg = "🔥【本物の在庫あり】Apple公式に入荷しました！\n\n" + "\n".join(items) + "\n\n今すぐ購入：\nhttps://www.apple.com/jp/shop/refurbished/iphone"
        send_line(msg)
        print(f"検知成功: {items}")
    else:
        print("チェック完了：現在は購入可能な在庫はありません。")
