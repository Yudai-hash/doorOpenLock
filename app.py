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
import time

duty = 30

GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.OUT)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(27,GPIO.OUT)
GPIO.setup(25,GPIO.OUT)
#GPIO.setup(27,GPIO.IN)

#50 Hz
p1 = GPIO.PWM(27,50)
p2 = GPIO.PWM(4,50)

p1.start(0)
p2.start(0)

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
    try:
        if lineRes == 'lock':
            #GPIO.output(4,True)
            #GPIO.output(27,False)
            p1.ChangeDutyCycle(duty)
            p2.ChangeDutyCycle(0)
            time.sleep(0.5)
            p1.ChangeDutyCycle(0)
            botRes = 'LOCK'
        elif lineRes == 'open':
            #GPIO.output(4,False)
            #GPIO.output(27,True)
            p1.ChangeDutyCycle(0)
            p2.ChangeDutyCycle(duty)
            time.sleep(0.5)
            p2.ChangeDutyCycle(0)
            botRes = 'OPEN'
        elif lineRes == 'stop':
            #GPIO.output(4,False)
            #GPIO.output(27,False)
            p1.ChangeDutyCycle(0)
            p2.ChangeDutyCycle(0)
            botRes = 'STOP'
        elif lineRes == 'lightup':
            GPIO.output(25,True)
            botRes = 'lightup'
        elif lineRes == 'lightdown':
            GPIO.output(25,False)
            botRes = 'lightdown'
        elif lineRes == 'check':
            if GPIO.input(27):
                botRes = 'CLOSE'
            else:
                botRes = 'OPEN'
    except KeyboardInterrupt:
        #print('stop')
        pass
        
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=botRes))
    #Clean might be a problem to get "please set pin numbering mode using GPIO.
    #.setmode(GPIO.BOARD) or GPIO.setmode(GPIO.BCM)"
    #    GPIO.cleanup()

if __name__ == "__main__":
    app.run()
    GPIO.cleanup()
