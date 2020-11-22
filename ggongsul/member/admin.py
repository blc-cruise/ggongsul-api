from django.contrib import admin

# Register your models here.
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("username", "is_staff")
