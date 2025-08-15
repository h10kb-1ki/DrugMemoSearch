from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import sqlite3

# 環境変数（Render）
CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

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
def handle_message(event):
    user_message = event.message.text.strip()
    reply_text = db_search(user_message)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

def db_search(keyword):
    db = sqlite3.connect('drug_memo.db')
    cur = db.cursor()

    cur.execute("""
        SELECT * FROM memo 
        WHERE drug LIKE ? OR tag LIKE ? OR memo LIKE ? 
        """, 
        [f'%{keyword}%', f'%{keyword}%', f'%{keyword}%']
        )
    results = cur.fetchall()
    cur.close()
    db.close()

    if len(results) == 0:
        return '該当データはありません！'
    else:
        txt = ''
        for result in results:
            txt += f'◼︎{result[1]}\n{result[3]}\n\n'
        return txt

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
