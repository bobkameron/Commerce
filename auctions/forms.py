from django import forms
from django.forms import ModelForm

from . models import Listing, Comment

from . models import MAX_LENGTH_CHAR_FIELD

class NewListingForm(ModelForm):

    class Meta:
        model = Listing 
        fields = ['title', 'description', 'image_url' , 'starting_price', 'category']

class NewBidForm(forms.Form):
    amount = forms.DecimalField(decimal_places=2, max_digits = 25, label = "New Bid Amount ($)")

class CloseListingForm(forms.Form):
    close_listing = forms.CharField(widget = forms.HiddenInput(), initial = "close_listing")

class NewCommentForm(ModelForm):
    class Meta:
        model = Comment 
        fields = ['text']