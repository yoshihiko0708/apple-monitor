import os
import requests
import re

# 通知したい機種のキーワード
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
        
        # 1. フィルター（サイドバー）のエリアを特定
        sidebar_match = re.search(r'fieldset role="group".*?iPhone', content, re.DOTALL)
        search_area = sidebar_match.group(0) if sidebar_match else content

        found_items = []
        
        # 2. 各機種の「入力要素（input）」と「ラベル」の塊を解析
        # Appleのサイトでは通常 <input ...> と <label ...> がセットになっています
        # 在庫がないものは input に 'disabled' が付いています
        
        # 各モデルごとにループ
        for model in TARGET_MODELS:
            # 正規表現の解説:
            # 1. <li ...> から </li> までの塊を探す
            # 2. その中に機種名（model）が含まれている
            # 3. かつ、その塊の中に 'disabled' という文字が含まれて「いない」
            
            # 商品ごとのリスト項目を取得
            items = re.findall(r'<li[^>]*>.*?</li>', search_area, re.DOTALL)
            
            for item in items:
                if model in item:
                    if 'disabled' not in item:
                        # 'disabled' が含まれていなければ「黒文字（有効）」と判定
                        found_items.append(f"📱{model}")
                        break
        
        return list(set(found_items))

    except Exception as e:
        print(f"解析エラー: {e}")
        return []

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
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    items = check_apple_store()
    if items:
        msg = "🔥【在庫あり】Apple公式で選択可能になりました！\n\n" + "\n".join(items) + "\n\n今すぐチェック：\nhttps://www.apple.com/jp/shop/refurbished/iphone"
        send_line(msg)
        print(f"検知しました: {items}")
    else:
        print("チェック完了：現在は選択可能な（黒文字の）対象在庫はありません。")
