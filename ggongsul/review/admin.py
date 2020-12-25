from django.contrib import admin

from ggongsul.review.models import Review, ReviewImage


class ReviewImageInline(admin.StackedInline):
    model = ReviewImage


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    inlines = [ReviewImageInline]
