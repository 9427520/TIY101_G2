import google.generativeai as genai
import os
import json
from io import BytesIO
from PIL import Image

from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    MessagingApiBlob,
    PostbackAction,
    QuickReply,
    QuickReplyItem
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent,
    PostbackEvent
)

app = Flask(__name__)

# ENV Config file
with open(json_file_path) as f:
    env = json.load(f)
configuration = Configuration(access_token=env['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(env['CHANNEL_SECRET'])
# 若不用讀檔的方法可以直接設api_key="your_gemini_api_key"
genai.configure(api_key=env["GOOGLE_API_KEY"])

with ApiClient(configuration) as api_client:
    line_bot_api = MessagingApi(api_client)
    line_bot_blob_api = MessagingApiBlob(api_client)


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
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=ImageMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        message_content = line_bot_blob_api.get_message_content(message_id=event.message.id)
        model = genai.GenerativeModel('gemini-1.0-pro-vision-latest')
        image = Image.open(BytesIO(message_content))
		#提示詞也可不設
		prompt='此為寵物健檢報告,請依圖片輸出表格數值'
        if prompt:
            response = model.generate_content([prompt,image])
		else :
            response = model.generate_content(image)	
		#print出結果可以看有無正確輸出	
        print(response.text)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response.text)]
        )
    )
	
if __name__ == "__main__":
    app.run()	
	