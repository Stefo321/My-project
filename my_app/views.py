from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DeleteView

from .forms import PostForm
from .models import Post


# View for displaying the list of posts
def post_list(request):
    posts = Post.objects.all()
    print("Posts in the database:", posts)
    return render(request, 'post_list.html', {'posts': posts})


# View for displaying the details of a single post
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'post_detail.html', {'post': post})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
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


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_confirm_delete.html'
    success_url = reverse_lazy('post_list')  # Redirect to post list after successful deletion

    def get_queryset(self):
        # Ensure only the author of the post can delete it
        return Post.objects.filter(author=self.request.user)
