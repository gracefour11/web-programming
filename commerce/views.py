from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms


from .models import *
import datetime

class NewListingForm(forms.Form):
    title = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder':'Enter Title','class':'col-sm-11',}))
    description = forms.CharField(required = True, widget=forms.Textarea(attrs={'placeholder':'Enter Description of Item','class':'col-sm-11'}))
    price = forms.CharField(required=True, widget=forms.NumberInput(attrs={'step':'0.01', 'min': '0'}))
    image_link = forms.CharField(required=True, widget=forms.URLInput())

def index(request):
    return render(request, "auctions/index.html", {"listings": Listing.objects.filter(winner=None)})


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


# create a listing once user is logged in
@login_required(login_url="login")
def createListing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        
        if form.is_valid():
            
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            price = form.cleaned_data["price"]
            image_link = form.cleaned_data["image_link"]
            user = request.user
            category_id = Category.objects.get(id=request.POST["categories"])
            listing = Listing.objects.create(category=category_id, title=title, description=description, user=user,
            price=price, image_link=image_link)
            starting_bid = Bid.objects.create(user=user, price=price, listing=listing)
        
        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, "auctions/createlisting.html", {
            "form": NewListingForm(),
            "categories": Category.objects.all()
        })


@login_required(login_url="login")
def listing_info(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    comments = Comment.objects.filter(listing=listing.id)
    user = request.user
    is_owner = True if listing.user == user else False
    category = Category.objects.get(category=listing.category)
    return listing, user, is_owner, category, comments


@login_required(login_url="login")
def viewListing(request, listing_id):
    info = listing_info(request, listing_id)
    listing, user, is_owner, category, comments = info[0], info[1], info[2], info[3], info[4]

    watch_items = WatchList.objects.filter(user=user, listing=listing.id)

    current_bid = Bid.objects.filter(listing=listing.id)
    current_bidder = current_bid.latest('user').user

    if current_bidder == user:
        current_bidder = None

    has_winner = False
    if listing.winner is not None:
        has_winner = True

    return render(request, "auctions/viewListing.html", {
        "user": user,
        "listing": listing,
        "watch_items": watch_items,
        "comments": comments,
        "is_owner":is_owner,
        "current_bidder": current_bidder,
        "has_winner": has_winner,
        "winner": listing.winner
    })


def bid(request, listing_id):
    info = listing_info(request, listing_id)
    listing, user, is_owner, category, comments = info[0], info[1], info[2], info[3], info[4]


    #if user submits a bid
    if request.method=="POST":
        bid = request.POST.get("bid")
        new_bid = float(bid)

        #check if new_bid is smaller or equal to current bid(listing.price)
        if new_bid <= listing.price:
            return render(request, "auctions/viewListing.html", {
                "listing": listing,
                "message": "Please ensure that Your Bid is higher than the current Bid!",
                "message_type": "danger",
                "comments": comments
            })
        
        # if new_bid is higher --> update in Listings and Bid tables
        else:
            #Update Listing
            listing.price = new_bid
            listing.save()

            #Remove current bid object from Bid table
            # current_bid_obj =  Bid.objects.filter(listing=listing.id)
            # if current_bid_obj:
            #     current_bid_obj.delete()

            #Add new bid object to Bid table
            new_bid_obj = Bid()
            new_bid_obj.user = request.user
            new_bid_obj.price = new_bid
            new_bid_obj.listing = listing
            new_bid_obj.save()

            return render(request, "auctions/viewListing.html", {
                "listing": listing,
                "message": "Your bid has been successfully added!",
                "message_type": "success",
                "comments": comments
            })

    else:
        return HttpResponseRedirect(reverse("index"))


@login_required(login_url="login")
def closeListing(request, listing_id):
    info = listing_info(request, listing_id)
    listing, user, is_owner, category, comments = info[0], info[1], info[2], info[3], info[4]
    listing.sold_date = datetime.datetime.now()
    winning_bid = Bid.objects.get(price=listing.price, listing=listing)
    winner = winning_bid.user
    listing.winner = winner
    is_winner = user == winner
    listing.save()

    return render(request, "auctions/closeListing.html", {
        "listing": listing,
        "category": category,
        "comments": comments,
        "is_owner": is_owner,
        "is_winner": is_winner,

    })

@login_required(login_url="login")
def addToWatchList(request, listing_id):
    info = listing_info(request, listing_id)
    listing, user, is_owner, category, comments = info[0], info[1], info[2], info[3], info[4]

    item = WatchList.objects.filter(listing=listing, user=user)
    
    if not item:
        WatchList.objects.create(user = user, listing = listing)
    
    return render(request, "auctions/viewListing.html", {
        "listing": listing,
        "category": category,
        "comments": comments, 
        "watching": WatchList.objects.get(user = user, listing = listing), 
        "is_owner": is_owner,
        "message": "This listing has been ADDED to your watchlist.",
        "message_type": "success"
    })

@login_required(login_url="login")
def removeFromWatchList(request, listing_id):
    info = listing_info(request, listing_id)
    listing, user, is_owner, category, comments = info[0], info[1], info[2], info[3], info[4]

    item = WatchList.objects.filter(listing=listing, user=user)
    
    if item:
        WatchList.objects.filter(user = user, listing = listing).delete()
    
    
    return render(request, "auctions/viewListing.html", {
        "listing": listing,
        "category": category,
        "comments": comments, 
        "watching": WatchList.objects.filter(user=user, listing=listing),
        "is_owner": is_owner,
        "message": "This listing has been REMOVED from your watchlist.",
        "message_type": "success"
    })


@login_required(login_url="login")
def viewWatchList(request, user_id):

    listing_ids = WatchList.objects.filter(user = request.user).values('listing')
    listings = Listing.objects.filter(id__in = listing_ids)
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

@login_required(login_url="login")
def addComment(request, listing_id):
    info = listing_info(request, listing_id)
    listing, user, is_owner, category, comments = info[0], info[1], info[2], info[3], info[4]

    if request.method=="POST":
        comment = request.POST.get("comment")
        if comment != "":
            Comment.objects.create(user=user, listing=listing, comment=comment)
        
        return render(request, "auctions/viewListing.html", {
            "listing": listing,
            "category": category,
            "comments": comments, 
            "is_owner": is_owner,
            "message": "Your comment has been posted",
            "message_type": "success"
        })
    
    return render(request, "auctions/viewListing.html", {
            "listing": listing,
            "category": category,
            "comments": comments, 
            "is_owner": is_owner,
    })

def category(request):
    listings = Listing.objects.filter(winner=None)
    category = None
    
    if request.method == "POST":
        category = request.POST["categories"]
        listings = Listing.objects.filter(category =category, winner=None)
    
    return render(request, "auctions/category.html", {
        "categories": Category.objects.all(),
        "category": Category.objects.get(id=category).category if category is not None else "",
        "listings": listings,
    })