from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.http.response import JsonResponse
import json

from .models import *
from . import forms

MAX_POSTS_PER_PAGE = 10

def index(request):
    unpaginated_posts = Post.objects.all().order_by('-created_dt')
    all_posts = paginate(request, unpaginated_posts)
    return render(request, "network/index.html", {
        'form': forms.CreatePostForm(),
        'all_posts': all_posts,
        "title": "All Posts",
        'remove_create_post': "False"
    })

def paginate(request, dataList):
    paginator = Paginator(dataList, MAX_POSTS_PER_PAGE)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)
    return page_obj


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def create_post(request):
    if request.method == "POST":
        form = forms.CreatePostForm(request.POST)
        if form.is_valid():
            contents = form.cleaned_data["contents"]
            if len(contents) > 0:
                user = User.objects.get(id=request.session['_auth_user_id'])
                post = Post(user=user, contents=contents)
                post.save()
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "network/createpost.html", {
                    "form": form,
                })
        else:
            return render(request, "network/createpost.html", {
                "form": form,
            })
    else:
        form = forms.CreatePostForm()
        return render(request, "network/createpost.html", {
            "form": form,
        })


@csrf_exempt
@login_required
def edit_post(request, id):
    if request.method == 'POST':
        post = Post.objects.get(id=id)
        data = json.loads(request.body)
        if data.get("body") is not None:
            post.contents = data["body"]
        post.save()
        return JsonResponse({"success": 'Post updated successfully.'}, status=204)
    return JsonResponse({"error": "POST request required."}, status=400)
            
@csrf_exempt
@login_required
def like(request, id):
    if request.method == 'POST':
        post = Post.objects.get(id=id)
        users_who_like_post = post.likes.all()
        request_user = request.user
        data = json.loads(request.body)
        if data.get("like") == 'true':
            post.likes.add(request_user)
        else:
            post.likes.remove(request_user)
        post.save()
        return JsonResponse({"likes": post.get_likes_count()})
    return JsonResponse({"error": "POST request required."}, status=400)


@login_required
def profile(request, username):
    request_user = request.user
    profile_user = User.objects.get(username=username)
    follow_list = request_user.follow_list.all()
    following_count = profile_user.get_following_count()
    follower_count = profile_user.get_follower_count()
    unpaginated_posts = Post.objects.filter(user=profile_user).order_by('-created_dt')
    all_posts = paginate(request, unpaginated_posts)
    is_following = False
    
    if profile_user in follow_list:
        is_following = True

    remove_create_post = "True"
    if request_user == profile_user:
        remove_create_post = "False"
    
    return render(request, "network/index.html", {
        'profile_user': profile_user,
        'following_count': following_count,
        'follower_count': follower_count,
        'all_posts': all_posts,
        'is_following': is_following,
        'is_profile_page': "True",
        'title': profile_user.username,
        'remove_create_post': remove_create_post
    })

@login_required
def follow(request, id):
    user = request.user
    target = User.objects.get(id=id)
    user.follow_list.add(target)
    user.save()
    return redirect(reverse('profile', kwargs={
        'username': target.username
    }))

@login_required
def unfollow(request, id):
    user = request.user
    target = User.objects.get(id=id)
    user.follow_list.remove(target)
    user.save()
    return redirect(reverse('profile', kwargs={
        'username': target.username
    }))

@login_required
def following(request):
    user = request.user
    follow_list = user.follow_list.all()
    unpaginated_posts = Post.objects.filter(user__in=follow_list).order_by('-created_dt')
    all_posts = paginate(request, unpaginated_posts)

    return render(request, "network/index.html", {
        'all_posts': all_posts,
        'title': "Following",
        'remove_create_post': "True"
    })



