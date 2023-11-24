from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings


from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TemplateSendMessage

import json

from base.models import User

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

    user_id = event.source.user_id
    user_message = event.message.text

    if user_message == "我愛三星":
        template_data_path = make_user_fav_actvities_json(user_id)
        print(f"{template_data_path=}")
        template_data = load_template_from_json(template_data_path)

        template_message = TemplateSendMessage(
            alt_text='SightPath推薦最適合你的活動',
            template=template_data
        )
        
        
        line_bot_api.reply_message(event.reply_token, template_message)
    # else:
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextMessage(text=f"你说的是: {user_message}")
    #     )


def load_template_from_json(json_file_path):
    with open(json_file_path, "r", encoding="utf-8") as file:
        template_data = json.load(file)
    return template_data


def make_user_fav_actvities_json(user_id):
    user = User.objects.get(line_user_id=user_id)
    
    max_columns = 10
    
    # top3 = user.top3.all().order_by("ord")
    # print(f"{top3=}")
    # nope_activities = user.nope_activity.all()
    # print(f"{nope_activities=}")
    
    like_activities = user.love_activity.all()
    
    data = {"type": "carousel",
            "columns": [],
            "imageAspectRatio": "rectangle",
            "imageSize": "cover"}
    
    batch_id = 1
    for activity in like_activities:
        if batch_id <= max_columns:
            backup_url = "https://sightpath.tw/static/images/mascot.png"
            # if len(activity.cover_img_url) < 60:
            #     img_url = activity.cover_img_url 
            # else:
            #     img_url = backup_url
            
            if activity.cover_img_url == "":
                img_url = backup_url
            else:
                img_url = activity.cover_img_url
                
            activity_url = f"https://www.accupass.com/event/{activity.eventIdNumber}"
            
            activity_column = {"thumbnailImageUrl": img_url,
                            "imageBackgroundColor": "#000000",
                            "title": f"{activity.name[:37]}...",
                            "text": f"{activity.summary[:57]}...",
                            "defaultAction": {"type": "uri",
                                                "label": "View detail",
                                                "uri": activity_url},
                                "actions": [{"type": "uri",
                                            "label": "詳細資料",
                                            "uri": activity_url}]}
            
            data["columns"].append(activity_column)

            batch_id += 1
        else:
            break
    downald_path = f"./static/messages/love_activities_user_{user_id}.json"
    with open(downald_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return downald_path