from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_LENGTH_CHAR_FIELD = 200

class User(AbstractUser):
    pass 


class Listing(models.Model):


    title = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD)
    description = models.TextField()
    
    image_url = models.TextField()
    
    starting_price = models.DecimalField(decimal_places=2, max_digits = 25)

    CATEGORY_CHOICES = [
        ('fashion', 'Fashion'   ),
        ('electronics', 'Electronics'),
        ('art', 'Art and Collectibles'),
        ('home', 'Home and Garden'),
        ('toys','Toys'),
        ('other', 'Other'),
    ] 

    category = models.CharField(max_length = 15, choices = CATEGORY_CHOICES, default = 'other')
        
    active = models.BooleanField()

    listing_user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'listings')

    watching = models.ManyToManyField(User, blank = True, related_name = "watchlist")


class Bid(models.Model):
    amount = models.DecimalField(decimal_places=2, max_digits = 25)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name = "bids")
    
    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name = "bids")

class Comment(models.Model):
    text = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name = 'comments')

    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name = 'comments')
