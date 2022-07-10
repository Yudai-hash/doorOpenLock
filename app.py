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

import RPi.GPIO as GPIO

duty = 80

GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.OUT)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(27,GPIO.OUT)
#GPIO.setup(27,GPIO.IN)



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
    #   GPIO.output(27,True)
    if lineRes == 'lock':
        GPIO.output(4,True)
        GPIO.output(17,False)
        #p1.ChangeDutyCycle(duty)
        #p2.ChangeDutyCycle(0)
        botRes = 'LOCK'
    elif lineRes == 'open':
        GPIO.output(4,False)
        GPIO.output(17,True)
        #p1.ChangeDutyCycle(0)
        #p2.ChangeDutyCycle(duty)
        botRes = 'OPEN'
    elif lineRes == 'check':
        if GPIO.input(27):
            botRes = 'CLOSE'
        else:
            botRes = 'OPEN'
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=botRes))
    #Clean might be a problem to get "please set pin numbering mode using GPIO.
    #.setmode(GPIO.BOARD) or GPIO.setmode(GPIO.BCM)"
    #    GPIO.cleanup()

if __name__ == "__main__":
    app.run()
