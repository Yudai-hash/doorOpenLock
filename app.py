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

class SG92_Class:
    #constractor
    def __init__(self,Pin,ZeroOffsetDuty):
        self.mPin = Pin
        self.mZeroOffsetDuty = ZeroOffsetDuty

        #Set the sermo GPIO mode
        GPIO.setup(self.mPin,GPIO.OUT)
        self.mPwm = GPIO.PWM(self.mPin,50)
    #set the position
    def SetPos(self,pos):
        duty = (12-2.5)/180*pos+2.5 + self.mZeroOffsetDuty
        self.mPwm.start(duty)
    #end the process
   # def Cleanup(self):
   #     self.SetPos(90)
   #     time.sleep(1)
   #     GPIO.setup(self.mPin,GPIO.IN)
        
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
    GPIO.setmode(GPIO.BCM)
    Servo = SG92_Class(Pin=4,ZeroOffsetDuty=0)
    try:
        if lineRes == 'lock':
            Servo.SetPos(0)
            botRes = 'LOCK'
        elif lineRes == 'open':
            Servo.SetPos(90)
            botRes = 'OPEN'
        elif lineRes == 'check':
            if GPIO.input(27):
                botRes = 'CLOSE'
            else:
                botRes = 'OPEN'
    except KeyboardInterrupt:
        #print('stop')
        pass
    #finally:
        #Servo.Cleanup()
        #GPIO.clean()
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=botRes))
    #Clean might be a problem to get "please set pin numbering mode using GPIO.
    #.setmode(GPIO.BOARD) or GPIO.setmode(GPIO.BCM)"
    #    GPIO.cleanup()

if __name__ == "__main__":
    app.run()
    GPIO.clean()
