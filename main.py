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
        "Referer": "https://www.apple.com/jp/",
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        content = res.text
        
        found_items = []

        # 1. ページを「商品カード」の単位で分割します
        # Appleのサイトで商品一つ分を区切る目印（classやliなど）で分割
        # 'rf-refurb-producttile' や 'refurbished-category-grid-item' を目印にします
        tiles = re.split(r'class="refurbished-category-grid-item|rf-refurb-producttile', content)
        
        for tile in tiles[1:]: # 最初の破片はヘッダーなので無視
            
            # 【在庫ありの絶対条件】
            # そのブロックの中に「価格(円)」と「購入系ボタン(選択/バッグに追加)」の両方があるか？
            # これがあれば、サイドバー（フィルタ）ではなく「本物の商品カード」です。
            if ("円" in tile) and ("選択" in tile or "バッグ" in tile or "購入" in tile):
                
                for model in TARGET_MODELS:
                    # そのブロックの中に指定した機種名が含まれているか
                    if model in tile:
                        # 商品名をより正確に抽出
                        name_search = re.search(r'data-related-product-name="([^"]+)"', tile)
                        if not name_search:
                            name_search = re.search(r'title="([^"]+)"', tile)
                        
                        full_name = name_search.group(1) if name_search else model
                        
                        # 価格をそのブロックの中からだけ抽出（他の商品の価格と混ざらない）
                        price_match = re.search(r'([0-9,]+円)', tile)
                        price = price_match.group(1) if price_match else "価格確認不可"
                        
                        found_items.append(f"📱{full_name} 【{price}】")
                        break # 一つのブロックに複数のモデル名は入らないので次へ

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
        msg = "🔥【入荷確定】Apple公式で在庫を検知しました！\n\n" + "\n".join(items) + "\n\n今すぐ購入：\nhttps://www.apple.com/jp/shop/refurbished/iphone"
        send_line(msg)
        print(f"検知成功: {items}")
    else:
        print("チェック完了：条件に一致する『購入可能な商品』はありませんでした。")
