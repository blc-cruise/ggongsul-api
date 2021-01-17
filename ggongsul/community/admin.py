from django.contrib import admin

from ggongsul.community.models import Post, Comment, PostImage


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = (
        PostImageInline,
        CommentInline,
    )
    exclude = ("longitude", "latitude")
    list_display = ("__str__", "total_comment_cnt", "total_attention_cnt", "is_deleted")
