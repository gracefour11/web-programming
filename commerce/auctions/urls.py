from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createListing", views.createListing, name="createListing"),
    path("listing/<str:listing_id>", views.viewListing, name="viewListing"),
    path("bid/<str:listing_id>", views.bid, name="bid"),
    path("closeListing/<str:listing_id>", views.closeListing, name="closeListing"),
    path("addToWatchList/<str:listing_id>", views.addToWatchList, name="addToWatchList"),
    path("removeFromWatchList/<str:listing_id>", views.removeFromWatchList, name="removeFromWatchList"),
    path("watchlist/<str:user_id>", views.viewWatchList, name="viewWatchList"),
    path("addComment/<str:listing_id>", views.addComment, name="addComment"),
    path("categories", views.category, name="categories"),
]
