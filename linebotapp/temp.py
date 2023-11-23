from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django.conf import settings

import json
import sys

from linebot.v3 import (
    WebhookParser
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
    TemplateMessage,
    LocationMessage,
    ImagemapMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)


channel_access_token = settings.LINE_CHANNEL_ACCESS_TOKEN
channel_secret = settings.LINE_CHANNEL_SECRET

# TODO: django error handling
# https://medium.com/@techWithAditya/middleware-magic-how-to-use-django-middleware-for-advanced-error-handling-and-exception-management-78573a27204e

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)

if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

configuration = Configuration(access_token=channel_access_token)
parser = WebhookParser(channel_secret)


# line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
# parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


@csrf_exempt
@require_POST
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        
        for event in events:
            if not isinstance(event, MessageEvent):
                continue
            if not isinstance(event.message, TextMessageContent):
                continue
            print(event)
            """
            type='message' source=UserSource(type='user', user_id='U3814bb2f841ea91686f752e33043483f') timestamp=1692764377416 mode=<EventMode.ACTIVE: 'active'> webhook_event_id='01H8G9X4SK3FP5WB4RD2CD04NB' delivery_context=DeliveryContext(is_redelivery=False) reply_token='5262a155e1794b2e918a096574240e93' message=TextMessageContent(type='text', id='469649763529392526', text='hi', emojis=None, mention=None)
            """
            print(event.message.text)
            if event.message.text == "test": 
                with ApiClient(configuration) as api_client:                       
                    line_bot_api = MessagingApi(api_client)
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text="測試")]
                        )
                    )
            elif event.message.text in ["活動推薦", "1"]:
                with ApiClient(configuration) as api_client:
                    with open("./static/messages/recommend_activities.json", "r", encoding="utf-8") as f:
                        res_json = json.load(f)
                        
                    activity_recommend_message = TemplateMessage.from_dict(res_json)

                    line_bot_api = MessagingApi(api_client)
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[activity_recommend_message,
                                      TextMessage(text="以上是根據你的個人資料及興趣所推薦的活動")]
                        )
                    )
            elif event.message.text == "Sitcon 學生社群大亂鬥-活動地點":
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[LocationMessage(title="Sitcon 學生社群大亂鬥",
                                                      address="台北市大安區基隆路四段43號",
                                                      latitude=25.013355480857506,
                                                      longitude=121.54060381718553)]
                        )
                    )
            elif event.message.text == "個人興趣分析":
                    with ApiClient(configuration) as api_client:
                        line_bot_api = MessagingApi(api_client)
                        line_bot_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=event.reply_token,
                                messages=[ImagemapMessage(originalContentUrl="https://raw.githubusercontent.com/weifish0/SightPath/master/static/images/persona_interests.png",
                                                          previewImageUrl="https://raw.githubusercontent.com/weifish0/SightPath/master/static/images/persona_interests.png"),
                                          TextMessage(text="")]
                            )
                        )
                # line_bot_api.reply_message_with_http_info(
                #     ReplyMessageRequest(
                #         reply_token=event.reply_token,
                #         messages=[TextMessage(text=event.message.text)]
                #     )
                # )

        print("收到訊息")
        return HttpResponse()
