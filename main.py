import os
import requests

# 通知したい機種のキーワード
TARGET_MODELS = ["iPhone 16", "iPhone 17"]

def check_apple_store():
    # ブラウザで見るのと同じURLを使用
    url = "https://www.apple.com/jp/shop/refurbished/iphone"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ja-JP,ja;q=0.9",
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status() # 404ならここでエラーへ飛ぶ
        
        # 取得したHTML（ページの文字全部）をテキストとして読み込む
        content = res.text
        
        found_items = []
        for model in TARGET_MODELS:
            # ページの中に機種名が含まれているか、単純に文字検索する
            if model in content:
                found_items.append(f"📱{model} (在庫あり、またはページに掲載されました)")
        
        return found_items

    except Exception as e:
        print(f"データ取得エラーが発生しました: {e}")
        return []

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
        # 重複を消して整理
        unique_items = list(set(items))
        msg = "🔥Apple公式に動きがありました！\n\n" + "\n".join(unique_items) + "\n\n確認はこちら：\nhttps://www.apple.com/jp/shop/refurbished/iphone"
        send_line(msg)
        print("在庫を検知し、LINEを送信しました。")
    else:
        print("チェック完了：現在は指定の機種は見つかりませんでした。")
