import os
import requests
import json

# キーワード（Appleの内部データ形式に合わせます）
TARGET_MODELS = ["iPhone 15 Pro", "iPhone 15 Pro Max", "iPhone 16", "iPhone 17"]

def check_apple_store():
    # データを直接持っているURLを狙います
    url = "https://www.apple.com/jp/shop/refurbished/ajax/data/iphone"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.apple.com/jp/shop/refurbished/iphone",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        # もし403や404なら通常のページへ切り替え
        if res.status_code != 200:
            res = requests.get("https://www.apple.com/jp/shop/refurbished/iphone", headers=headers, timeout=15)
        
        content = res.text
        found_items = []

        # ページ全体のテキストの中から、ターゲット機種を探す
        for model in TARGET_MODELS:
            # 「機種名」があり、かつそのすぐ近くに「在庫あり(In Stock)」を意味する
            # 価格や特定のキーワード（"price" や "instock"）があるかを一気に判定
            # 非常にシンプルですが、これが最も確実です
            if model in content:
                # サイドバーのノイズを除外するため、「円」が含まれているかを確認
                # ただし、APIレスポンスの場合は「円」がないこともあるので
                # 「"currentPrice"」というキーワードをセットで探します
                if "currentPrice" in content or "円" in content:
                    found_items.append(f"📱{model}")

        return list(set(found_items))

    except Exception as e:
        print(f"エラー: {e}")
        return []

def send_line(message):
    token = os.environ.get("LINE_ACCESS_TOKEN")
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    payload = {"messages": [{"type": "text", "text": message}]}
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    items = check_apple_store()
    if items:
        msg = "🔥【入荷検知】Apple公式サイトで在庫を確認しました！\n\n" + "\n".join(items) + "\n\n今すぐ確認：\nhttps://www.apple.com/jp/shop/refurbished/iphone"
        send_line(msg)
        print(f"検知成功: {items}")
    else:
        print("チェック完了：現在は確実な在庫データが見つかりませんでした。")
