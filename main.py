import os
import requests
import json
import re

# 通知したい機種のキーワード
TARGET_MODELS = ["15 Pro", "15 Pro Max", "16", "17"]

def check_apple_store():
    # 誰でもアクセスできるメインページをターゲットにします
    url = "https://www.apple.com/jp/shop/refurbished/iphone"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ja-JP,ja;q=0.9",
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        content = res.text
        
        # Appleのページ内にある "tiles" という変数に格納された在庫データを抽出します
        # これはブラウザが商品を表示するために使っている「生のリスト」です
        found_items = []
        
        # ページ内のJavaScriptデータ（JSON部分）を正規表現で切り出します
        data_match = re.search(r'window\.REFURB_GRID_DATA\s*=\s*({.*?});', content, re.DOTALL)
        
        if data_match:
            # 生データが見つかった場合（JSON解析）
            raw_json = data_match.group(1)
            data = json.loads(raw_json)
            products = data.get('tiles', [])
            
            for product in products:
                # 商品名と価格、在庫状況を取得
                name = product.get('title', '')
                # 商品カードとして存在している＝在庫がある証拠
                for target in TARGET_MODELS:
                    if target in name:
                        price = product.get('price', '')
                        found_items.append(f"📱{name} ({price})")
                        break
        else:
            # 生データが見つからない場合の予備手段（HTMLから直接抽出）
            # 商品カードのタイトル属性と価格が両方あるものだけを抜く
            blocks = content.split('class="refurbished-category-grid-item')
            for block in blocks[1:]: # 最初の分割はゴミなので飛ばす
                for target in TARGET_MODELS:
                    if target in block and "円" in block:
                        # リンクやサイドバーではなく、商品詳細が含まれるカードのみ
                        name_match = re.search(r'data-related-product-name="([^"]+)"', block)
                        if name_match:
                            name = name_match.group(1)
                            found_items.append(f"📱{name}")
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
        msg = "🔥【本物の在庫あり】Apple公式に入荷しました！\n\n" + "\n".join(items) + "\n\n今すぐ購入：\nhttps://www.apple.com/jp/shop/refurbished/iphone"
        send_line(msg)
        print(f"検知成功: {items}")
    else:
        print("チェック完了：現在は購入可能な在庫はありません。")
