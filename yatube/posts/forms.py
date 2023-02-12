from django import forms
from .models import Post, Comment
# Group

from .validators import validate_not_empty


# GROUP_CHOICES = ([['','---------']] +
# list(Group.objects.values_list('id', 'title')))

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': ('Текст поста'),
            'group': ('Группа')
        }
        help_texts = {
            'text': ('Текст нового поста'),
            'group': ('Группа, к которой будет относиться пост')
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, validators=[validate_not_empty])
    email = forms.EmailField(required=False)
    subject = forms.CharField(max_length=100, required=False)
    body = forms.CharField(widget=forms.Textarea, required=False)
    is_answered = forms.BooleanField(initial=False, required=False)
