from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers

from ggongsul.community.models import Post, Comment
from ggongsul.member.serializers import MemberSerializer


class PostSerializer(serializers.ModelSerializer):
    def validate(self, attrs: dict):
        attrs["member"] = self.context["request"].user
        return attrs

    class Meta:
        model = Post
        exclude = ("is_deleted", "deleted_on")


class CommentSerializer(serializers.ModelSerializer):
    def validate(self, attrs: dict):
        attrs["member"] = self.context["request"].user
        return attrs

    class Meta:
        model = Comment
        exclude = ("is_deleted", "deleted_on")


class CommentInfoSerializer(serializers.ModelSerializer):
    member = MemberSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["member", "body", "created_on"]


class PostShortInfoSerializer(serializers.ModelSerializer):
    member = MemberSerializer(read_only=True)
    is_tabbed = serializers.SerializerMethodField()

    def get_is_tabbed(self, obj: Post):
        member = self.context["request"].user
        if isinstance(member, AnonymousUser):
            return False
        return obj.attentions.filter(member=member, is_deleted=False).exists()

    class Meta:
        model = Post
        fields = [
            "member",
            "short_body",
            "image",
            "longitude",
            "latitude",
            "total_attention_cnt",
            "total_comment_cnt",
            "is_tabbed",
            "created_on",
        ]


class PostDetailInfoSerializer(serializers.ModelSerializer):
    comments = CommentInfoSerializer(read_only=True, many=True)
    is_tabbed = serializers.SerializerMethodField()

    def get_is_tabbed(self, obj: Post):
        member = self.context["request"].user
        if isinstance(member, AnonymousUser):
            return False
        return obj.attentions.filter(member=member, is_deleted=False).exists()

    class Meta:
        model = Post
        fields = [
            "member",
            "body",
            "image",
            "longitude",
            "latitude",
            "total_attention_cnt",
            "total_comment_cnt",
            "is_tabbed",
            "comments",
            "created_on",
        ]
