from django.shortcuts import render, redirect
from django import forms
import markdown2
from . import util
import random as R

# Class to create a new form for char input
class SearchForm(forms.Form):
    search = forms.CharField(label="Search")

# Class of a form to create a New entry 
class CreateForm(forms.Form):
    title = forms.CharField(max_length=100, required=True)
    content = forms.CharField(widget=forms.Textarea, required=True)

# Class of a form to Edit existing entry
class EditForm(forms.Form):
    my_textarea = forms.CharField(widget=forms.Textarea)

# Main page
def index(request):
    # If user inputs value in form
    if request.method == 'POST':
        form = SearchForm(request.POST)

        if form.is_valid():

            # search is a variable with it's value as the input from user
            search = form.cleaned_data["search"]

            # If search page do'es not exist take user to page with list of pages as it's substring
            if not util.get_entry(search):
                return render(request, "encyclopedia/index.html", {
                    "searched": True,
                    "entries": substrings(search),
                    "form": SearchForm()})
            
            # Redirect user to searched page
            return redirect("entry", name=search)
        
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()})

# Page of markdown content of "name" ex. /wiki/python or /wiki/css
def entry(request, name):
    markdowner = markdown2.Markdown()

    # markdown data from "name" as the page name
    en = util.get_entry(name)

    return render(request, "encyclopedia/entry.html", {
        # .convert() converts the markdown inputs to html
        'data': markdowner.convert(en) if en else None,
        'title': name,
        "form": SearchForm()})

# Create new page
def create(request):
    if request.method == 'POST':
        form = CreateForm(request.POST)

        if form.is_valid():

            # Take title and content from users input
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            # If title already exists then send an error message
            if util.get_entry(title):
                return render(request, "encyclopedia/create.html", {
                    "form": SearchForm(),
                    "create": form,
                    "error_message": 'Entry with this title already exists.'})
            
            # Save the new entry page in the dataset and redirect to that page
            util.save_entry(title, content)
            return redirect("entry", name=title)
        
    return render(request, "encyclopedia/create.html", {
        "form": SearchForm(),
        "create": CreateForm()})

# Edit existing page
def edit(request, title):
    if request.method == 'POST':
        form = EditForm(request.POST)

        if form.is_valid():

            # Take the new edited content from user
            new_content = form.cleaned_data["my_textarea"]

            # Save the changes
            util.save_entry(title, new_content)

            # Redirect user to edited page
            return redirect("entry", name=title)
        
    # Form ( textarea ) with existing contents which user can change
    edit = EditForm(initial={"my_textarea": util.get_entry(title)})
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": SearchForm(),
        "edit": edit})

# Go to a random existing entry
def random(request):
    en = R.choice(util.list_entries())
    return redirect("entry", name=en)

## Helper Function to get list of entries with "string" as it's substring
def substrings(string):
    string = string.lower()
    l = [entry for entry in util.list_entries() if string in entry.lower()]
    return l