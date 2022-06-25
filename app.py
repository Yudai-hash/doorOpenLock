from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('4wmhUDo4We9wDOTNtwj0ts+S7HIU/8iBEk92oAXXlVhXvhHWskJlfk+RlDKrTGIx81FzYUFIVHCuEmk+eBkWx1UF9Gu4UmIo4X+knQDT7YFNhUytmA5/jnhrz+gbRk0zw3rXO8l3TvrwaEDVkODhygdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('29d9c8034e5a6bc9fd2e0d7217c760d7')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    lineRes = event.message.text
    botRes = '鍵を施錠、開錠できます'

    if lineRes == '123':
        GPIO.output(4,1)
        botRes = '開錠しました'
    if lineRes == '456':
        GPIO.output(4,0)
        botRes = '施錠しました'
    if lineRes == '789':
        if GPIO.input(17):
            botRes = '開錠中'
        else:
            botRes = '施錠中'
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=botRes))


if __name__ == "__main__":
    app.run()
