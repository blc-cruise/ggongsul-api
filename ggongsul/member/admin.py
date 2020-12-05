from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Member


@admin.register(Member)
class MemberAdmin(UserAdmin):

    list_display = ("username", "is_staff")
