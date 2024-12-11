import markdown
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Post, Comment, Category, Notification, LikeDislike
from .forms import PostForm, CommentForm


# views.py

class PostListView(ListView):
    model = Post
    template_name = 'post_list.html'
    context_object_name = 'posts'
    paginate_by = 10  # Adjust this as needed

    def get_queryset(self):
        queryset = Post.objects.all()
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(categories__name=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['is_admin'] = self.request.user.groups.filter(name='Admin').exists()  # Admin check
        context['selected_category'] = self.request.GET.get('category', '')  # Pass the selected category to template
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        comments = post.comments.all()

        # Convert markdown content
        post.content = markdown.markdown(post.content)
        for comment in comments:
            comment.text = markdown.markdown(comment.text)

        context.update({
            'comments': comments,
            'form': CommentForm(),
            'categories': post.categories.all(),
            'liked': LikeDislike.objects.filter(user=self.request.user, post=post, is_like=True).exists(),
            'disliked': LikeDislike.objects.filter(user=self.request.user, post=post, is_like=False).exists(),
            'is_admin_or_author': self.request.user.groups.filter(
                name='Admin').exists() or post.author == self.request.user,
        })
        return context


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'

    def form_valid(self, form):
        # Ensure the post's author is the current user unless they are an admin
        if not self.request.user.groups.filter(name='Admin').exists():
            form.instance.author = self.request.user
        else:
            form.instance.author = self.request.user
        response = super().form_valid(form)
        return redirect(self.object.get_absolute_url())  # Redirect to post detail after creation


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'

    def form_valid(self, form):
        post = form.instance
        # Only allow the author or an admin to update the post
        if post.author != self.request.user and not self.request.user.groups.filter(name='Admin').exists():
            messages.error(self.request, "You are not authorized to edit this post.")
            return redirect('post_list')  # Redirect to post list if not authorized
        response = super().form_valid(form)
        return redirect(self.object.get_absolute_url())  # Redirect to the updated post detail page


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'post_confirm_delete.html'
    success_url = '/'  # Change this to the URL where you want to redirect after delete

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != self.request.user and not self.request.user.groups.filter(name='Admin').exists():
            messages.error(self.request, "You are not authorized to delete this post.")
            return redirect('post_list')  # Redirect to the post list if not authorized
        return super().delete(request, *args, **kwargs)


class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'comment_form.html'

    def form_valid(self, form):
        comment = self.get_object()
        if comment.author != self.request.user:
            messages.error(self.request, "You are not authorized to edit this comment.")
            return redirect('post_detail', pk=comment.post.pk)
        return super().form_valid(form)


class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'comment_confirm_delete.html'

    def get_success_url(self):
        comment = self.get_object()
        return reverse('post_detail', kwargs={'pk': comment.post.pk})

    def delete(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != self.request.user:
            messages.error(self.request, "You are not authorized to delete this comment.")
            return redirect('post_detail', pk=comment.post.pk)
        return super().delete(request, *args, **kwargs)


class LikeDislikeView(View):
    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])
        like_dislike = request.POST.get('like_dislike')

        # Check if the user has already voted (like or dislike)
        existing_vote = LikeDislike.objects.filter(user=request.user, post=post).first()

        if existing_vote:
            # If the user has already voted, update their vote
            if like_dislike == 'like' and not existing_vote.is_like:
                existing_vote.is_like = True  # Switch to like
            elif like_dislike == 'dislike' and existing_vote.is_like:
                existing_vote.is_like = False  # Switch to dislike
            existing_vote.save()  # Save the updated vote
        else:
            # If no previous vote, create a new vote (like or dislike)
            LikeDislike.objects.create(user=request.user, post=post, is_like=(like_dislike == 'like'))

        return redirect('post_detail', pk=post.pk)


@login_required
def user_profile(request):
    user = request.user
    posts = Post.objects.filter(author=user)
    comments = Comment.objects.filter(author=user)

    context = {
        'user': user,
        'posts': posts,
        'comments': comments,
    }

    return render(request, 'user_profile.html', context)


# Function to send notifications when a comment is added
def create_notification(user, post=None, comment=None, message=''):
    Notification.objects.create(
        user=user,
        post=post,
        comment=comment,
        message=message
    )


# Function to handle comment creation and send notification
@login_required  # Ensure the user is logged in before posting a comment
def post_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':  # Ensure we are handling a POST request
        form = CommentForm(request.POST)  # Pass the POST data to the form
        if form.is_valid():
            comment = form.save(commit=False)  # Don't commit immediately to assign post and author
            comment.post = post
            comment.author = request.user
            comment.save()  # Save the comment

            # Optionally, create a notification for the post author
            create_notification(post.author, post=post,
                                message=f"{request.user.username} commented on your post: {post.title}")

            return redirect('post_detail', pk=post.pk)  # Redirect back to the post detail page
        else:
            # If the form is not valid, re-render the page with the form errors
            return render(request, 'post_detail.html', {'post': post, 'form': form})

    # If the request is not POST, it should be redirected or show an error
    return redirect('post_list')


def post_by_category(request):
    category_name = request.GET.get('category')
    posts = Post.objects.filter(categories__name=category_name) if category_name else Post.objects.all()

    context = {
        'posts': posts,
        'categories': Category.objects.all(),
    }
    return render(request, 'post_list.html', context)


def post_edit(request, slug=None):
    if slug:
        post = get_object_or_404(Post, slug=slug)
    else:
        post = None

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post successfully updated!')
            return redirect('post_list')  # Redirect to a post list or any other view
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PostForm(instance=post)

    return render(request, 'post_form.html', {'form': form})


# Create or Edit Comment
def comment_edit(request, post_slug, comment_id=None):
    post = get_object_or_404(Post, slug=post_slug)
    comment = None
    if comment_id:
        comment = get_object_or_404(Comment, id=comment_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            new_comment.save()
            messages.success(request, 'Comment successfully posted!')
            return redirect('post_detail', slug=post.slug)  # Adjust this to your post detail URL
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CommentForm(instance=comment)

    return render(request, 'comment_form.html', {'form': form, 'post': post})
