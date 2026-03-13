import os
import requests

def test_push():
    token = os.environ.get("LINE_ACCESS_TOKEN")
    user_id = os.environ.get("USER_ID")
    
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    # テスト送信
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": "テスト通知です！これが届けば設定は完璧です。"}]
    }
    res = requests.post(url, headers=headers, json=payload)
    print(f"ステータスコード: {res.status_code}")
    print(f"レスポンス: {res.text}")

if __name__ == "__main__":
    test_push()
