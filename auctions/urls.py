from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name='create_listing'),
    path("listing/<int:listing_id>", views.show_listing, name='listing'),
    path("add_watchlist/<int:listing_id>", views.add_watchlist, name='add_watchlist'),
    path("make_bid/<int:listing_id>", views.make_bid, name='make_bid'),
    path("close_listing/<int:listing_id>", views.close_listing, name='close_listing'),
    path("inactive_listings", views.inactive_listings, name="inactive_listings"),
    path("add_comment/<int:listing_id>", views.add_comment, name="add_comment"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),

]
