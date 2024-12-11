from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views
from my_project import settings
from . import views
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    CommentUpdateView,
    CommentDeleteView,
    LikeDislikeView,  # Ensure LikeDislikeView is imported if using it
)

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/new/', PostCreateView.as_view(), name='create_post'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='post_list'), name='logout'),
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('comment/<int:pk>/edit/', CommentUpdateView.as_view(), name='comment_edit'),
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
    path('profile/', views.user_profile, name='user_profile'),

    # Add URL for posting comments
    path('post/<int:pk>/comment/', views.post_comment, name='post_comment'),

    # Updated URL for Like/Dislike functionality
    path('like_dislike/<int:pk>/', LikeDislikeView.as_view(), name='like_dislike'),

    # implement category filtering by URL, keep the next line
    path('category/', views.post_by_category, name='post_by_category'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
