# Generated by Django 4.2.16 on 2024-12-10 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0005_category_notification_likedislike_post_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='post',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddConstraint(
            model_name='likedislike',
            constraint=models.UniqueConstraint(fields=('user', 'post'), name='unique_like_post'),
        ),
        migrations.AddConstraint(
            model_name='likedislike',
            constraint=models.UniqueConstraint(fields=('user', 'comment'), name='unique_like_comment'),
        ),
    ]