from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TemplateSendMessage

import json

channel_access_token = settings.LINE_CHANNEL_ACCESS_TOKEN
channel_secret = settings.LINE_CHANNEL_SECRET

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@csrf_exempt
@require_POST
def callback(request):
    signature = request.META['HTTP_X_LINE_SIGNATURE']
    body = request.body.decode('utf-8')

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return HttpResponseForbidden("Invalid signature")

    return HttpResponse("OK", status=200)


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_message = event.message.text

    if user_message == "2":
        # 如果用户发送的消息是 "2"，回复 TemplateMessage，从 JSON 文件加载模板数据
        template_message = load_template_from_json("template_data.json")
        line_bot_api.reply_message(event.reply_token, template_message)
    else:
        # 如果用户发送的是其他消息，可以进行其他处理或回复
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=f"你说的是: {user_message}")
        )


def load_template_from_json(json_file_path):
    with open(json_file_path, "r", encoding="utf-8") as file:
        template_data = json.load(file)

    return TemplateSendMessage(**template_data)