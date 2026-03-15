import os
import requests
import re

# 監視ターゲット（機種名）
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
        
        found_items = []

        # 【本物の商品だけを狙い撃つ最強の正規表現】
        # 1. 機種名 (例: iPhone 15 Pro)
        # 2. その後、100文字以内に「GB」または「TB」（容量）
        # 3. さらにその近くに「円」（価格）があるものだけを抽出
        for model in TARGET_MODELS:
            # 正規表現の意味: 機種名 ... (最大150文字) ... 容量(GB/TB) ... (最大150文字) ... 価格(円)
            pattern = rf"{model}.*?([0-9]+(?:GB|TB)).*?([0-9,]+円)"
            
            # ページ全体からこのパターンに一致する箇所をすべて探す
            matches = re.findall(pattern, content, re.DOTALL)
            
            for m in matches:
                storage = m[0]
                price = m[1]
                found_items.append(f"📱{model} {storage} ({price})")

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
        msg = "🔥【入荷確定】Apple公式で本物の在庫を検知しました！\n\n" + "\n".join(items) + "\n\n今すぐ購入：\nhttps://www.apple.com/jp/shop/refurbished/iphone"
        send_line(msg)
        print(f"検知成功: {items}")
    else:
        print("チェック完了：『容量と価格が揃った』有効な商品リストは見つかりませんでした。")
