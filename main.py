import os
import requests
import re

# キーワード（少し短くして、一致しやすくします）
TARGET_MODELS = ["15 Pro", "15 Pro Max", "16", "17"]

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

        # 1. ページ内の全商品を「ブロック」として切り出す
        # 在庫がある商品は必ず "refurbished-category-grid-item" という塊の中に名前と価格があります
        blocks = content.split('refurbished-category-grid-item')
        
        for block in blocks[1:]: # 最初の分割はヘッダーなので飛ばす
            for model in TARGET_MODELS:
                # 【判定条件を極限までシンプルに】
                # 「機種名」が含まれており、かつ同じブロック内に「円」が含まれていれば
                # それはサイドバーではなく「商品カード」であると断定します
                if model in block and "円" in block:
                    # 商品名をきれいに抜き出す
                    # data-related-product-name または title 属性を探す
                    name_search = re.search(r'data-related-product-name="([^"]+)"', block)
                    if not name_search:
                        name_search = re.search(r'title="([^"]+)"', block)
                    
                    product_name = name_search.group(1) if name_search else f"iPhone {model}"
                    
                    # サイドバーの残骸でないことを文字数でチェック（本物は名前が長い）
                    if len(product_name) > 10:
                        found_items.append(f"📱{product_name}")
                        break

        # もしブロックで見つからない場合、ページ全体から「価格付きの機種名」を強引に探す（予備）
        if not found_items:
            for model in TARGET_MODELS:
                # 例: iPhone 15 Pro ... 124,800円 というパターン
                if re.search(rf"{model}.*?[\d,]+円", content, re.DOTALL):
                    found_items.append(f"📱{model} (在庫あり)")

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
        # ログを詳細にして、何が見えているかヒントを出します
        print("チェック完了：現在は条件（機種名＋価格）に合う在庫は見つかりませんでした。")
