from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Comment

def index(request):
    return render(request, "auctions/index.html",{
        'listings': Listing.objects.filter(active = True)
    })

@login_required
def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        'listings': Listing.objects.filter( watching__id = request.user.id   )
    })

@login_required
def create_listing(request):
    return render(request, "auctions/create_listing.html")

def categories(request):
    return render(request, "auctions/categories.html")

def category(request, category_string):
    
    return HttpResponse("Category")

def listing (request, listing_id):
    errorMessage = None 
    listing = Listing.objects.get(id = listing_id)
    if not listing:
        errorMessage = "Invalid Listing"

    return render(request, "auctions/listing.html", {
        'listing': listing,
        'message' : errorMessage 
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
