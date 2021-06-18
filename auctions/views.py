from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from .models import User, Listing, Bid, Comment
from django.contrib.auth.decorators import login_required

from django import forms

class ListingForm(forms.Form):
    title = forms.CharField(label='Title', max_length=100)
    description = forms.CharField(label='Description', max_length=100)
    category = forms.ChoiceField(choices=(
        ('Books','Books',),
        ('Electronics','Electronics'),
        ('Others','Others')))
    price = forms.IntegerField(min_value=0)
    image_url = forms.CharField(label="Link an image", max_length=512, min_length=0, required=False)

class BidForm(forms.Form):
    bid_value = forms.IntegerField(label="Bid Amount", min_value=0)


def index(request):
    # Show only active listings.
    listings = Listing.objects.filter(active=True)
    users = User.objects.all()
    return render(request, "auctions/index.html",{
        "listings":listings,
        "show_active":True,
    })

def inactive_listings(request):
    listings = Listing.objects.filter(active=False)
    return render(request, "auctions/index.html",{
        "listings":listings,
        "show_active":False,
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

@login_required
def create_listing(request):
    # Check if user is logged in.
    if request.user.is_authenticated:
        if request.method == "POST":
            print("Entering listing view with post request.")
            # init instance of listing form, populate with post data.
            form = ListingForm(request.POST)
            if form.is_valid():
                # Get data from form
                title = form.cleaned_data['title']
                description = form.cleaned_data['description']
                category = form.cleaned_data['category']
                price = form.cleaned_data['price']
                image_url = form.cleaned_data['image_url']
                # Create instance of model
                l = Listing(user=request.user, title=title, description=description,
                    category=category, price=price, image_url=image_url)
                l.save()
            
                return render(request, "auctions/create_listing.html",{
                    "message": "Listing created.",
                    "listing_form":ListingForm(),})
            else:
                return render(request, "auctions/create_listing.html",{
                    "message": "Form is invalid."})
        else: #if request is not a post method
            return render(request, "auctions/create_listing.html", {
            "listing_form":ListingForm()
        })

    else:
        return render(request, "auctions/create_listing.html", {
            "message":"Please log in first"
        })

def check_if_watchlisted(request, listing_id):
    my_watchlist = request.user.watchlist.all()
    my_listing = Listing.objects.get(pk=listing_id)
    is_watchlisted = False
    if my_listing in my_watchlist:
        is_watchlisted = True
    return is_watchlisted

def check_if_show_close(request, listing_id):
    # cur user and listing creator must be same.
    my_listing = Listing.objects.get(pk=listing_id)
    creator = my_listing.user
    my_user = request.user
    if creator != my_user:
        return False
    # cur listing must not already be closed.
    if my_listing.active != True:
        return False
    return True

def check_if_winning_user(request, listing_id):
    # Returns true if listing is closed, AND, user who win the listing is the currently logged in user.
    my_listing = Listing.objects.get(pk=listing_id)
    print(my_listing.active)
    if my_listing.active == True:
        return False
    # Get the user who bid the highest.
    highest_bidder = my_listing.bids.order_by('-value')[0].user
    if len(my_listing.bids.all()) > 0:
        highest_bidder = my_listing.bids.order_by('-value')[0].user
        if highest_bidder == request.user:
            print("check if winner user is returning True")
            return True
    return False
    
def get_highest_bid_value(some_listing):
    if len(some_listing.bids.all()) > 0:
        return max(some_listing.price, int(some_listing.bids.order_by('-value')[0].value))
    else:
        return some_listing.price

def show_listing(request, listing_id):
    # Get watchlist status
    context = {"listing":"", "is_watchlisted":"", "bid_form":'', "show_close_button":"", "is_winner_user":"", "comments":""}
    my_listing = Listing.objects.get(pk=listing_id)
    context["listing"] = my_listing
    comments = my_listing.comments.all().reverse()
    context["comments"] = comments
    # Check if listing is watchlisted by user.
    if request.user.is_authenticated:
        is_watchlisted = check_if_watchlisted(request, listing_id) 
        show_close_button = check_if_show_close(request, listing_id) # show close button if user is the one who made the listing.
        is_winning_user = check_if_winning_user(request, listing_id)
        context["is_watchlisted"] = is_watchlisted
        context["show_close_button"] = show_close_button
        context["is_winning_user"] = is_winning_user
        context["bid_form"] = BidForm()
    return render(request, "auctions/listing.html", context)

@login_required
def add_watchlist(request, listing_id):
    # Handles adding and removing from watchlist.
    if request.user.is_authenticated:
        if request.method=="POST":
            cur_user = request.user
            # Get instance of the listing.
            my_listing = Listing.objects.get(pk=listing_id)
            if request.POST['watchlist_submit']=='add':
                cur_user.watchlist.add(my_listing)
                cur_user.save()
                return HttpResponseRedirect(reverse("listing", args=[listing_id]))
            elif request.POST['watchlist_submit']=='remove':
                cur_user.watchlist.remove(my_listing)
                cur_user.save()
                return HttpResponseRedirect(reverse("listing", args=[listing_id]))


@login_required
def make_bid(request, listing_id):
    # Handles the submission of bid_form POST request.
    if request.user.is_authenticated:
        if request.method=="POST":
            # Get user's bid.
            form = BidForm(request.POST)
            if form.is_valid():
                # Get data from form
                user_bid = int(form.cleaned_data['bid_value'])
            # Get all the bids for current listing.
            my_listing = Listing.objects.get(pk=listing_id)
            #print("---- debug make_bid. user_bid {}  my_listing {}".format(user_bid, my_listing))
            if user_bid <= get_highest_bid_value(my_listing):
                # Return to listing page with error message.
                message = "Please bid at least {}".format(get_highest_bid_value(my_listing)+1)
                is_watchlisted = check_if_watchlisted(request, listing_id)
                return render(request, "auctions/listing.html", {
                    "listing":my_listing,
                    "is_watchlisted": is_watchlisted,
                    "bid_form": form,
                    "message":message,
                })
            else:
                # User bid is valid. 
                #Write to  the Bid model.
                b = Bid(user=request.user, listing=my_listing, value=user_bid)
                b.save()
                # Update listing.price
                my_listing.price = user_bid
                my_listing.save()
                is_watchlisted = check_if_watchlisted(request, listing_id)
                message = "Bid of {} placed.".format(user_bid)
                return render(request, "auctions/listing.html", {
                    "listing":my_listing,
                    "is_watchlisted": is_watchlisted,
                    "bid_form": form,
                    "message":message,
                })
                # Return to the listing page
    return show_listing(request, listing_id)

@login_required
def close_listing(request, listing_id):
    # Change listing.active to False.
    my_listing = Listing.objects.get(pk=listing_id)
    my_listing.active = False
    my_listing.save()    
    # Render the page of the listing again.
    return show_listing(request, listing_id)    


def add_comment(request, listing_id):
    print("--Add comment debug. Comment data: {} ".format(request.POST.get("comment_text")))
    my_listing = Listing.objects.get(pk=listing_id)
    if request.method=="POST":
        comment_data = request.POST.get('comment_text')
        c = Comment(user=request.user, listing=my_listing, comment_text=comment_data)
        c.save()
    return show_listing(request, listing_id)

def watchlist(request):
    my_user = request.user
    watchlist = my_user.watchlist.all()
    context = {"watchlist":watchlist}
    return render(request, "auctions/watchlist.html", context)


def categories(request):
    categories = ["Electronics", "Books", "Others"]
    if request.method != "POST":
        return render(request, "auctions/categories.html", {
            "categories":categories
        })
    else: # get post data
        #selected_category = request.POST['selected_category']
        #print("Debug categories(): Selected category is {}".format(selected_category))
        category_name = request.POST['selected_category']
        selected_category = Listing.objects.filter(category=category_name)
        return render(request, "auctions/categories.html", {
            "categories":categories,
            "selected_category":selected_category,
            "category_name":category_name,
        })


