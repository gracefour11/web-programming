
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createpost", views.create_post, name="createpost"),
    path("edit/<int:id>", views.edit_post, name="editpost"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("follow/<int:id>", views.follow, name="follow"),
    path("unfollow/<int:id>", views.unfollow, name="unfollow"),
    path("following", views.following, name="following"),
    path("like/<int:id>", views.like, name="like"),
    path("unlike/<int:id>", views.like, name="unlike")
]
