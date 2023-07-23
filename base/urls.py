from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.login_page, name="login_page"),
    path("regitster/", views.register_page, name="register_page"),
    path("logout/", views.logout_user, name="logout_user"),
    path("profile/<str:pk>/", views.profile, name="profile"),
    path("room/<str:pk>/", views.room, name="room"),
    path("create_room/", views.create_room, name="create_room"),
    path("update_room/<str:pk>/", views.update_room, name="update_room"),
    path("delete_room/<str:pk>/", views.delete_room, name="delete_room"),
    path("delete_message/<str:pk>/", views.delete_message, name="delete_message"),
    path("edit_profile/<str:pk>/", views.edit_profile, name="edit_profile"),
    path("chatroom_home/", views.chatroom_home, name="chatroom_home"),
    path("", views.home_page, name="home_page"),
]