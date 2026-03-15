import os
import requests
import re
import json

# 通知したい機種のキーワード
TARGET_MODELS = ["iPhone 15 Pro", "iPhone 15 Pro Max", "iPhone 16", "iPhone 17"]

def check_apple_store():
    url = "https://www.apple.com/jp/shop/refurbished/iphone"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        content = res.text
        
        # Appleのサイト内にある「現在のフィルタ状態」のデータを抽出
        # この中には、現在「有効（黒文字）」なフィルタのIDが並んでいます
        found_items = []
        
        # 1. ページ全体から「どの機種が現在有効か」を定義しているJSON部分を探す
        # 非常にマニアックですが、'tiles' や 'filters' というデータ構造を狙います
        for model in TARGET_MODELS:
            # 「機種名」と、そのすぐ近くに「在庫あり」を示す属性があるか
            # または、単純に機種名が含まれる「商品カード」がHTML内に実在するかを厳密にチェック
            
            # 商品ブロックの区切り（商品ごとの個別データ）
            # 在庫がある商品は必ず "refurbished-category-grid-no-js" または特定のタグ内に名前があります
            # 特に「価格」がセットになっているものだけを抽出
            pattern = rf'data-related-product-name="[^"]*{model}[^"]*".*?[\d,]+円'
            if re.search(pattern, content, re.DOTALL):
                found_items.append(f"📱{model}")
        
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
        msg = "🔥【本物の在庫あり】Apple公式に入荷しました！\n\n" + "\n".join(items) + "\n\n今すぐ購入：\nhttps://www.apple.com/jp/shop/refurbished/iphone"
        send_line(msg)
        print(f"検知成功: {items}")
    else:
        # ログを詳細にして、何が起きているか把握できるようにします
        print("チェック完了：現在は『価格が表示されている』対象在庫はありません。")
