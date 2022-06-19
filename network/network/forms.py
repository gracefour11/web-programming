from django import forms
from .models import User


class CreatePostForm(forms.Form):
    contents =forms.CharField(label="",required= False, widget= forms.Textarea
    (attrs={'placeholder':'What\'s happening?','class':'col-sm','style':'top:1rem,margin:10rem'}))
