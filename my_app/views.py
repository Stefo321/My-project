from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DeleteView

from .forms import PostForm, CommentForm
from .models import Post, Comment


# View for displaying the list of posts
def post_list(request):
    # Check if the user is an Admin
    is_admin = request.user.groups.filter(name='Admin').exists()

    # If the user is an Admin, they can see all posts
    if is_admin:
        posts = Post.objects.all()
    else:
        # Regular users can only see their own posts
        posts = Post.objects.filter(author=request.user)

    # Pass both posts and is_admin to the template
    return render(request, 'post_list.html', {'posts': posts, 'is_admin': is_admin})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()

    # Check if the user is in the 'Admin' group
    is_admin = request.user.groups.filter(name='Admin').exists()
    # Check if the user is either an admin or the author of the post
    is_admin_or_author = is_admin or (post.author == request.user)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'is_admin': is_admin_or_author  # Pass the admin check to the template
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # Set the author to the logged-in user
            post.save()
            return redirect('post_list')  # Redirect to the post list after creation
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'post_form.html'
    success_url = reverse_lazy('post_list')  # Redirect to the post list page after a successful update

    def form_valid(self, form):
        # Ensure that only the user who created the post can update it
        if form.instance.author != self.request.user:
            return self.handle_no_permission()
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != self.request.user:
            return HttpResponseForbidden("You are not allowed to edit this post.")
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_confirm_delete.html'
    success_url = reverse_lazy('post_list')  # Redirect to post list after successful deletion

    def get_queryset(self):
        # Ensure only the author of the post can delete it
        return Post.objects.filter(author=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != self.request.user:
            return HttpResponseForbidden("You are not allowed to delete this post.")
        return super().dispatch(request, *args, **kwargs)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    fields = ['text']
    template_name = 'comment_form.html'

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post.pk})

    def form_valid(self, form):
        # Ensure only the author can edit the comment
        if form.instance.author != self.request.user:
            return HttpResponseForbidden("You are not allowed to edit this comment.")
        return super().form_valid(form)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'comment_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post.pk})

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != self.request.user:
            return HttpResponseForbidden("You are not allowed to delete this comment.")
        return super().dispatch(request, *args, **kwargs)


@login_required
def user_profile(request):
    # Get all posts and comments of the logged-in user
    posts = Post.objects.filter(author=request.user)
    comments = Comment.objects.filter(author=request.user)

    return render(request, 'user_profile.html', {
        'user': request.user,
        'posts': posts,
        'comments': comments
    })
