from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 

from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage

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
    TextMessage
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

if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')

configuration = Configuration(access_token=channel_access_token)
parser = WebhookParser(channel_secret)


# line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
# parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

@csrf_exempt
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

            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=event.message.text)]
                    )
                )
                
            # if isinstance(event, MessageEvent):  # 如果有訊息事件
            #     line_bot_api.reply_message(  # 回復傳入的訊息文字
            #         event.reply_token,
            #         TextSendMessage(text=event.message.text)
            #     )
            
            # line_bot_api.reply_message(
            #         ReplyMessageRequest(
            #             reply_token=event.reply_token,
            #             messages=[message]
            #         )
            #     )
            
        return HttpResponse("收到訊息")
    
    else:
        return render(request, "linebotapp/callback_page.html")
        # return HttpResponseBadRequest()
