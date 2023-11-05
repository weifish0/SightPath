from django.urls import path, include
from . import views

urlpatterns = [
    # 帳號登入
    path('accounts/', include('allauth.urls')),
    path("login/", views.login_page, name="login_page"),
    path("regitster/", views.register_page, name="register_page"),
    path("logout/", views.logout_user, name="logout_user"),
    
    path("profile/<str:pk>/", views.profile, name="profile"),
    path("room/<str:pk>/", views.room, name="room"),
    path("create_room/", views.create_room, name="create_room"),
    
    path("update_room/<str:pk>/", views.update_room, name="update_room"),
    path("delete_room/<str:pk>/", views.delete_room, name="delete_room"),
    path("pin_room/<str:pk>/", views.pin_room, name="pin_room"),
    path("unpin_room/<str:pk>/", views.unpin_room, name="unpin_room"),
    
    path("delete_message/<str:pk>/", views.delete_message, name="delete_message"),
    path("edit_profile/<str:pk>/", views.edit_profile, name="edit_profile"),
    path("chatroom_home/", views.chatroom_home, name="chatroom_home"),
    path("competition_info/<str:pk>", views.competition_info, name="competition_info"),
    path("find_competitions/", views.find_competitions, name="find_competitions"),
    path("settings/", views.platform_config, name="platform_config"),
    path("home_update/", views.home_update, name="home_update"),
    path("embvec/<str:isourtag>/<str:pk>/", views.embvec, name="embvec"),
    path("", views.home_page, name="home_page"),
   

    path("about/", views.about, name="about"),
    path("persona/", views.persona)
]