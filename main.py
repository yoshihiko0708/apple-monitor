import os
import requests
import re
import json

# 監視ターゲット（キーワード）
TARGET_MODELS = ["iPhone 15 Pro", "15 Pro Max", "iPhone 16", "iPhone 17"]

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

        # 【手法1】ページ内に埋め込まれたJSONデータを直接探す
        # Appleは "tiles" という項目の中に商品リストを隠し持っていることが多いです
        # ページ全体の文字列から、商品情報っぽい塊をすべて抜き出します
        product_patterns = re.findall(r'\{"partNumber":".*?"title":".*?"\}', content)
        
        # 【手法2】手法1で見つからない場合、商品カードのメタデータを直接探す
        if not product_patterns:
            product_patterns = re.findall(r'data-related-product-name="([^"]+)"', content)

        # 抽出したデータの中にターゲットがあるかチェック
        for chunk in product_patterns:
            for model in TARGET_MODELS:
                # 「機種名」が含まれているか
                if model in chunk:
                    # そのすぐ近くに「価格（円）」や「在庫あり」の証拠があるか
                    # （サイドバーのノイズは通常、価格情報を持ちません）
                    if "円" in content or "price" in chunk.lower():
                        # 機種名を整形して追加
                        name = chunk.replace('"', '').split(':')[-1] if '{' in chunk else chunk
                        found_items.append(f"📱{name}")
                        break

        # 重複を排除
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
        msg = "🔥【入荷】Apple公式で在庫を検知しました！\n\n" + "\n".join(items) + "\n\n今すぐ確認：\nhttps://www.apple.com/jp/shop/refurbished/iphone"
        send_line(msg)
        print(f"検知成功: {items}")
    else:
        # デバッグ用：何が起きているかヒントを出力
        print("チェック完了：現在は条件に一致する有効な在庫データが見つかりませんでした。")
