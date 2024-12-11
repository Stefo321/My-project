from django.contrib import admin
from .models import Post, Profile


# Restrict Post management to admins
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'status')  # Add status field to list display
    list_filter = ('author', 'created_at', 'status')  # Add 'status' to filter options
    search_fields = ('title', 'content')
    ordering = ('created_at',)  # Order by created_at by default

    # Ensure that only admins can edit posts
    def has_change_permission(self, request, obj=None):
        if obj:
            return obj.author == request.user or request.user.is_superuser
        return True

    def has_delete_permission(self, request, obj=None):
        if obj:
            return obj.author == request.user or request.user.is_superuser
        return True

    # Custom action to mark selected posts as published
    def make_published(modeladmin, request, queryset):
        queryset.update(status='published')  # Example action for updating the status of selected posts

    make_published.short_description = "Mark selected posts as published"

    actions = [make_published]  # Add the custom action


admin.site.register(Post, PostAdmin)


# Profile Admin customization
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'website')
    ordering = ('user',)  # Order profiles by the associated user

    # Make sure only admins can see and edit Profile
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

