from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from django.db.models import Count, Max
from . forms import NewListingForm , NewBidForm, CloseListingForm, NewCommentForm

from .models import User, Listing, Bid, Comment

emptyMessage = "empty_message"
heading = "heading"
DEFAULT_BID_ERROR_MESSAGE = "Please submit valid bid amount with max 2 decimal places. The bid amount must be\
            greater than the current price if there are bids, or greater than or equal to current price if there aren't bids."

def index(request):
    return render(request, "auctions/index.html",{
        'listings': Listing.objects.filter(active = True),
        emptyMessage : "No Active Listings",
        heading: "Active Listings",
        'message':None
    })

@login_required
def watchlist(request):
    return render(request, "auctions/index.html", {
        'listings': Listing.objects.filter( watching__id = request.user.id   ),
        emptyMessage: "No Listings are currently in your Watchlist. To add items to your watchlist click on an active listing and add it to your watchlist.",
        heading: 'Your Watchlist',
        'message':None 
    })

@login_required
def watchlist_add(request, listing_id ):
    listing = None 
    try: 
        listing = Listing.objects.get(pk = listing_id)
        request.user.watchlist.add(listing)
    except Listing.DoesNotExist:
        pass 
    return HttpResponseRedirect(reverse('listing', args = [listing_id]))

@login_required
def watchlist_remove(request,listing_id):
    listing = None 
    try: 
        listing = Listing.objects.get(pk = listing_id)
        if listing.watching.filter(username = request.user.username ).exists():
            request.user.watchlist.remove(listing)
    except Listing.DoesNotExist:
        pass 
    return HttpResponseRedirect(reverse('listing', args = [listing_id]))

@login_required
def create_listing(request):
    if request.method == "POST":
        form = NewListingForm( request.POST)
        
        if form.is_valid():
            starting_price = form.cleaned_data['starting_price']
            if starting_price >= 0: 
                title, description, image_url, category =  form.cleaned_data['title'], form.cleaned_data['description'], \
                    form.cleaned_data['image_url'], form.cleaned_data['category']  

                new_listing = Listing(title = title, description = description, image_url = image_url, starting_price = starting_price,
                category = category, listing_user = request.user)
                new_listing.save()
                return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "auctions/create_listing.html",{
                'form': form, 
                'message': 'Please resubmit a valid form. All fields are required except the image url. The starting price must be nonnegative.'
            })
    else:
        return render(request, "auctions/create_listing.html", {
            'form': NewListingForm ()
        })

def categories(request):
    return render(request, "auctions/categories.html", {
        'categories': Listing.CATEGORY_CHOICES,
        heading: 'Auction Categories'
    })

def category(request, category_string):
    '''
    category_string must be among the list of choices in Listing.CATEGORIES
    '''
    errorMessage = None 
    if category_string not in Listing.CATEGORIES:
        errorMessage = "This is not a valid category"
    
    string_rep = "" 
    if not errorMessage: string_rep = Listing.CATEGORIES[category_string]

    return render(request, "auctions/index.html", {
        'message': errorMessage,
        'listings': Listing.objects.filter(category = category_string, active = True ),
        emptyMessage: "No Listings in this Category",
        heading: "Active Auction Listings in Category: "+ string_rep,
    })

def check_listing_rep(listing):
    listing.number_bids = listing.bids.count()
    listing.highest_bid 

def listing (request, listing_id):
    
    errorMessage = None 
    listing = None 
    category = None 
    in_watchlist = False 
    close_listing_form = None 
    comments = None 
    try: 
        listing = Listing.objects.get(id = listing_id)
        # yet to be implemented
        # check_listing_rep(listing)

        category = Listing.CATEGORIES[listing.category]
        in_watchlist = listing.watching.filter(username = request.user.username ).exists()
        if listing.active and listing.listing_user == request.user:
            close_listing_form = CloseListingForm() 
    except Listing.DoesNotExist:
        pass 

    if not listing:
        errorMessage = "Invalid Listing"

    bid_form = NewBidForm()
    bid_message = None 
    
    comment_form = NewCommentForm() 

    if request.method == "POST":
        posted_comment_form = NewCommentForm(request.POST)
        if posted_comment_form.is_valid() and listing:
            new_comment = Comment(text= posted_comment_form.cleaned_data['text'] , listing = listing, 
            user = request.user )
            new_comment.save() 
        else: 
            close_form = CloseListingForm(request.POST)
            if close_form.is_valid() and request.user == listing.listing_user and listing.active:
                listing.active = False 
                listing.save()
                close_listing_form = None 

            elif listing.active :
                bid_form = NewBidForm(request.POST  )
                bid_amount = None 
                
                if bid_form.is_valid():
                    bid_amount = bid_form.cleaned_data['amount'] 
                    if (listing.number_bids > 0 and listing.highest_bid.amount < bid_amount ) or \
                        (listing.number_bids == 0 and bid_amount >= listing.starting_price) :
                        new_bid = Bid(amount = bid_amount, listing = listing, user = request.user )
                        new_bid.save()

                        try: 
                            old_high_bid = listing.highest_bid 
                            old_high_bid.highest_bid_for_listing = None 
                            listing.highest_bid = None 
                            listing.save()
                            old_high_bid.save() 
                        except:
                            pass 

                        listing.highest_bid = new_bid
                        listing.number_bids = listing.bids.count() 
                        listing.save()
                        listing.highest_bid.save()
                        
                        bid_message = "Congratulations you have entered a bid for this item."
                    else:
                        bid_message = DEFAULT_BID_ERROR_MESSAGE
                else:
                    bid_message = DEFAULT_BID_ERROR_MESSAGE

                if not bid_message:
                    bid_form = NewBidForm()

    if listing:
        comments_query = listing.comments.all()
        comments = []
        for comment in comments_query:
            comments.append(comment)

    return render(request, "auctions/listing.html", {
        'listing': listing,
        'message' : errorMessage,
        'category': category,
        'in_watchlist' : in_watchlist,
        "new_bid_form" : bid_form,
        'bid_message': bid_message,
        'close_listing_form': close_listing_form,
        'comments':comments,
        'comment_form': comment_form
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
