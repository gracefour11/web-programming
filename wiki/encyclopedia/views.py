from django.shortcuts import render, redirect
from markdown2 import markdown
from django.http import HttpResponseRedirect
from django import forms
from . import util
from random import randint


class NewPageForm(forms.Form):
    title = forms.CharField(label='Title', required=True, widget=forms.TextInput(attrs={'placeholder':'Enter Title','class':'col-sm-11', 'style':'left:1rem'}))
    content = forms.CharField(label='Markdown Content', required = True, widget=forms.Textarea(attrs={'placeholder':'Enter markdown content','class':'col-sm-11','style':'top:1rem'}))

class EditPageForm(forms.Form):
    title = forms.CharField(label='Title', required=True, widget=forms.HiddenInput)
    content = forms.CharField(label='Markdown Content', required = True, widget=forms.Textarea(attrs={'placeholder':'Enter markdown content','class':'col-sm-11','style':'top:1rem'}))



def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# Entry Page
def entry(request, title):
    content_md = util.get_entry(title) # in markdown format

    if content_md is None:
        content_md = "This page does not exist!"

        return render(request, "encyclopedia/error.html", {
            "content": content_md,
            "title": title
        })
        
    
    content_html = markdown(content_md) #convert markdown to html

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": content_html,
    })

# Search
def search(request):
    query = request.GET.get('q', '') # looks for a GET parameter named q and returns an empty string if that parameter wasnt submitted.

    if query in util.list_entries():
        # redirects to the wiki/query page if query is inside the list of entries
        
        return HttpResponseRedirect("wiki/"+query)
    
    else:
        # redirects to a list of entries with titles containing query in its title string
        # e.g. 'py' in 'python'

        possible_entry_list = [] # empty list to store the possible entries that have the query as a substring

        for entry in util.list_entries():
            if entry.lower().startswith(query.lower()): # convert both query substring and entry string to lowercase
                possible_entry_list.append(entry)

        if not possible_entry_list:
            content = "The page \'" + query + "\' does not exist. There were no results matching that query."
            
            return render(request, "encyclopedia/error.html", {
                "content": content,
                "title": query
            })

        else: 
            return render(request, "encyclopedia/index.html", {
                "entries": possible_entry_list
            })

# Create new page
def create(request):
    if request.method == 'POST':
        new_form = NewPageForm(request.POST)
        if not new_form.is_valid():
            return render(request, "encyclopedia/create.html", {
                "form": new_form,
                "message": "Title or content is missing. Please ensure that you provide both Title and Content."
            })
        else:
            title = new_form.cleaned_data["title"]
            content = new_form.cleaned_data["content"]
            
            for name in util.list_entries():
                if title.lower() == name.lower():
                    return render(request, "encyclopedia/create.html", {
                        "form": NewPageForm(),
                        "message": "Page with title: '"+title+"' already exists in Wiki Encyclopedia. Please try again."
                    })
            util.save_entry(title, content)

            return redirect("encyclopedia:entry", title=title)

    return render(request, "encyclopedia/create.html", {
        "form": NewPageForm()
    })


# Edit page
def edit(request, title):
    # get content
    content = util.get_entry(title)
    
    #initialise the edit_form
    edit_form = EditPageForm(initial={'title':title, 'content':content})

    if request.method == 'POST':
        edit_form = EditPageForm(request.POST)
        
        if edit_form.is_valid():
            title = edit_form.cleaned_data["title"]
            content = edit_form.cleaned_data["content"]
            util.save_entry(title, content)

            content_html = markdown(content)

            return render(request, "encyclopedia/entry.html", {
                "title": title,
                "content": content_html
            })
    
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": edit_form
    })

#get random entry page
def random(request):
    
    list_of_entries = util.list_entries()
    random_entry = list_of_entries[randint(0, len(list_of_entries)-1)]

    return redirect('encyclopedia:entry', title=random_entry)

        




