from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name = 'watchlist'),
    path("watchlist/add/<int:listing_id>", views.watchlist_add, name = "watchlist_add"),
    path("watchlist/remove/<int:listing_id>", views.watchlist_remove, name = "watchlist_remove"),

    path("create_listing", views.create_listing, name = 'create_listing'),
    path('categories', views.categories, name = 'categories' ), 
    path('categories/<category_string>', views.category, name = 'category' ),
    path('listing/<int:listing_id>', views.listing, name = 'listing'),
]
