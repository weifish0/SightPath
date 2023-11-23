from django.urls import path, include
from . import views

urlpatterns = [
    # 帳號登入系統
    path('accounts/', include('allauth.urls')),
    path("login/", views.login_page, name="login_page"),
    path("regitster/", views.register_page, name="register_page"),
    path("logout/", views.logout_user, name="logout_user"),
    path("line_login_settings/", views.line_login_settings, name="line_login_settings"),
    
    
    # 個人檔案系統 Persona
    path("profile/<str:pk>/", views.profile, name="profile"),
    path("edit_profile/<str:pk>/", views.edit_profile, name="edit_profile"),
    path("embvec/<str:isourtag>/<str:pk>/", views.embvec, name="embvec"),
    path("delete_data/<str:pk>/", views.delete_data, name="delete_data"),
    path("persona/", views.persona),
    path("save_persona/", views.save_persona),
    path("save_model/", views.save_model),
    path("top3/", views.save_top3),
    
    # 討論串系統
    path("room/<str:pk>/", views.room, name="room"),
    path("create_room/", views.create_room, name="create_room"),
    path("update_room/<str:pk>/", views.update_room, name="update_room"),
    path("delete_room/<str:pk>/", views.delete_room, name="delete_room"),
    path("pin_room/<str:pk>/", views.pin_room, name="pin_room"),
    path("unpin_room/<str:pk>/", views.unpin_room, name="unpin_room"),
    path("delete_message/<str:pk>/", views.delete_message, name="delete_message"),
    path("chatroom_home/", views.chatroom_home, name="chatroom_home"),
    path('likeroom/<int:room_id>/', views.like_post, name='like_room'),
    
    # 找比賽
    path("competition_info/<str:pk>", views.competition_info, name="competition_info"),
    path("find_competition/", views.find_competition, name="find_competition"),
    path("find_activity/", views.find_activity, name="find_activity"),
    
    # 用戶偏好設定
    path("settings/", views.platform_config, name="platform_config"),

    # 首頁
    path("", views.home_page, name="home_page"),
    path("home_update/", views.home_update, name="home_update"),
    

    # 關於我們
    path("about/", views.about_page, name="about_page"),
    
    # test
    # path("t/", views.test_views)
]