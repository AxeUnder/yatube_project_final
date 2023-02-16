# posts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
# from django.core.cache import cache
# from django.urls import reverse_lazy
# from django.views.generic import CreateView


from .models import Post, Group, User, Follow
from .forms import PostForm, ContactForm, CommentForm
from .utils import paginator


@cache_page(60 * 20)
def index(request):
    template = 'posts/index.html'
    posts_list = Post.objects.all().select_related('author')
    page_obj = paginator(request, posts_list, 10)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    page_obj = paginator(request, posts_list, 10)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    profile = get_object_or_404(User, username=username)
    user_posts = profile.posts.all()
    user_follower = Follow.objects.filter(
        author=profile
    )
    page_obj = paginator(request, user_posts, 10)
    following = request.user.is_authenticated and \
        Follow.objects.filter(
            user=request.user,
            author=profile
        ).exists()
    context = {
        'profile': profile,
        'user_posts': user_posts,
        'page_obj': page_obj,
        'username': username,
        'following': following,
        'user_follower': user_follower
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    post_detail = Post.objects.filter(pk=post_id)
    comment = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'post_detail': post_detail,
        'comment': comment,
        'form': form
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    # Получите пост и сохраните его в переменную post.
    post = get_object_or_404(Post, pk=post_id)
    post_detail = Post.objects.filter(pk=post_id)
    form = CommentForm(request.POST or None)
    template = 'posts/post_detail.html'
    comment = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'post_detail': post_detail,
        'comment': comment
    }
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    template = 'posts/create_post.html'
    context = {'form': form}
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', request.user.username)
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    is_edit = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=is_edit
    )
    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': is_edit
    }

    if request.user != is_edit.author:
        return redirect('posts:post_detail', is_edit.pk)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', is_edit.pk)
    return render(request, template, context)


@login_required
def user_contact(request):
    form = ContactForm()
    template = 'posts/contact.html'
    context = {'form': form}
    # Проверяем, получен POST-запрос или какой-то другой:
    if request.method != 'POST':
        return render(request, template, context)
    if not form.is_valid():
        return render(request, template, context)
    # Создаём объект формы класса ContactForm
    # и передаём в него полученные данные
    # Если все данные формы валидны - работаем с "очищенными данными" формы
    # Берём валидированные данные формы из словаря form.cleaned_data
    form = ContactForm(request.POST)
    name = form.cleaned_data['name']
    email = form.cleaned_data['email']
    subject = form.cleaned_data['subject']
    message = form.cleaned_data['body']
    is_answered = form.cleaned_data['is_answered']
    form = name, email, subject, message, is_answered
    # При необходимости обрабатываем данные
    # сохраняем объект в базу
    # form.save()
    return redirect('/thank-you/')


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    template = 'posts/follow.html'
    page_obj = paginator(request, post_list, 10)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect('posts:profile', username=username)
    follower, follower_new = Follow.objects.get_or_create(
        user=request.user,
        author=author
    )
    if follower or follower_new is True:
        return redirect('posts:profile', username=username)
    Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect('posts:profile', username=username)
    following = get_object_or_404(
        Follow,
        user=request.user,
        author=author
    )
    following.delete()
    return redirect('posts:profile', username=username)
