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
        
        # 1. サイドバー（フィルター）のHTMLブロックを特定
        # 「モデル」という見出しから始まるセクションを抽出
        sidebar_section = ""
        sidebar_match = re.search(r'fieldset role="group".*?iPhone', content, re.DOTALL)
        if sidebar_match:
            sidebar_section = sidebar_match.group(0)
        else:
            # セクションが見つからない場合は安全のため全体を対象にする
            sidebar_section = content

        found_items = []
        
        # 2. サイドバー内のリンク（<a>タグ）をすべて抽出
        # <a ...><span>機種名</span></a> のような構造を探します
        links = re.findall(r'<a[^>]*>(.*?)</a>', sidebar_section, re.DOTALL)
        
        for link_text in links:
            for model in TARGET_MODELS:
                # リンクのテキストの中に機種名が含まれているか
                # かつ、その機種名がターゲットと一致するか
                if model in link_text:
                    found_items.append(f"📱{model}")
                    break # このリンクで一つ見つかれば十分
        
        return list(set(found_items)) # 重複を除去

    except Exception as e:
        print(f"データ取得エラー: {e}")
        return []

def send_line(message):
    token = os.environ.get("LINE_ACCESS_TOKEN")
    if not token: return
    
    # 全員に一斉送信するモード
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
        msg = "🔥【在庫復活】Apple公式で選択可能になりました！\n\n" + "\n".join(items) + "\n\n今すぐチェック：\nhttps://www.apple.com/jp/shop/refurbished/iphone"
        send_line(msg)
    else:
        print("チェック完了：現在はリンクが有効な対象在庫はありません。")
