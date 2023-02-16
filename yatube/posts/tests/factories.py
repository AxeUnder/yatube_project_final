from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Post, Group


User = get_user_model()


_counter = 0


def unique_string(prefix=""):
    global _counter
    _counter += 1
    return prefix + str(_counter)


title = unique_string("title")
slug = unique_string("slug")
description = unique_string("description")
text = unique_string("post")
group = None
image = None


def post_create(author, text=text, group=group, image=image):
    return Post.objects.create(
        text=text,
        author=author,
        group=group,
        image=image
    )


def group_create(title=title, slug=slug, description=description):
    return Group.objects.create(
        title=title,
        slug=slug,
        description=description
    )


def user_create(username):
    return User.objects.create_user(username)


def url_rev(url, **kwargs):
    return reverse(url, kwargs=kwargs)
