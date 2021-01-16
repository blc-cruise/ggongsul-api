from django.contrib import admin

from ggongsul.community.models import Post, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = (CommentInline,)
    exclude = ("longitude", "latitude")
    list_display = ("__str__", "total_comment_cnt", "total_attention_cnt", "is_deleted")
