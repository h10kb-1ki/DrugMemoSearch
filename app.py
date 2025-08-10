from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import sqlite3

# 環境変数や直接埋め込みでもOK（本番は環境変数推奨）
CHANNEL_ACCESS_TOKEN = "YOUR_CHANNEL_ACCESS_TOKEN"
CHANNEL_SECRET = "YOUR_CHANNEL_SECRET"

app = Flask(__name__)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def db_search(keyword):
    db = sqlite3.connect('drug_memo.db')
    cur = db.cursor()

    cur.execute("""
        SELECT * FROM T_memo 
        WHERE drug LIKE ? OR tag LIKE ? OR memo LIKE ? 
        """, 
        [f'%{keyword}%', f'%{keyword}%', f'%{keyword}%']
        )
    results = cur.fetchall()
    cur.close()
    db.close()

    if len(results) == 0:
        txt = '該当データはありません。'
    else:
        txt = ''
        for i in range(len(results)):
            txt = txt + f'◼︎{results[i][1]}\n{results[i][3]}\n\n'
    return txt

def handle_message(event):
    user_message = event.message.text.strip()
    reply_text = db_search(user_message)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
