from django.contrib.auth.models import AbstractUser
from django.db import models

# User model that represents each user of the application (inherits from AbstractUser)
class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.category}"


# Listings
class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=300)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="winner")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listing_category")
    image_link = models.URLField(default='google.com')
    created_date = models.DateTimeField(auto_now_add=True)
    sold_date = models.DateTimeField(auto_now=False, blank=True, null=True)
    

    def __str__(self):
        return f"Item: {self.title} posted by {self.user}"


# Bids
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Current bid on item: {self.listing} is ${self.price} made by {self.user}"


# Comments
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    comment = models.CharField(max_length=64) 
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.comment} commented by {self.user} at {self.time}"


# Watchlists
class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    

    def __str__(self):
        return f"Item: {self.listing.id} watched by {self.user.username}" 
