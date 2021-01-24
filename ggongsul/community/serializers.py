from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ggongsul.community.models import Post, Comment, PostImage
from ggongsul.member.serializers import MemberSerializer


class PostSerializer(serializers.ModelSerializer):
    def validate(self, attrs: dict):
        attrs["member"] = self.context["request"].user
        return attrs

    class Meta:
        model = Post
        fields = [
            "id",
            "member",
            "body",
            "longitude",
            "latitude",
            "images",
        ]
        extra_kwargs = {"member": {"required": False, "allow_null": True}}


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = [
            "id",
            "image",
        ]


class CommentSerializer(serializers.ModelSerializer):
    member_detail = serializers.SerializerMethodField()

    def get_member_detail(self, obj: Comment):
        if obj.member is None:
            return None
        return MemberSerializer(obj.member).data

    def validate(self, attrs: dict):
        attrs["member"] = self.context["request"].user

        view = self.context["view"]
        post_look_up_keyword = getattr(view, "post_look_up_keyword", "post_id")
        post_id = view.kwargs.get(post_look_up_keyword, None)
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise ValidationError(_(f"post id: {post_id} is not exists!"))

        attrs["post"] = post
        return attrs

    class Meta:
        model = Comment
        exclude = ("is_deleted", "deleted_on")
        extra_kwargs = {
            "member": {"required": False, "allow_null": True, "write_only": True}
        }


class CommentInfoSerializer(serializers.ModelSerializer):
    member = MemberSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "member", "body", "created_on"]


class PostShortInfoSerializer(serializers.ModelSerializer):
    member = MemberSerializer(read_only=True)
    is_tabbed = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    def get_is_tabbed(self, obj: Post):
        member = self.context["request"].user
        if isinstance(member, AnonymousUser):
            return False
        return obj.attentions.filter(member=member, is_deleted=False).exists()

    def get_images(self, obj: Post):
        images = []
        for img in obj.images.all():
            images.append(img.image.url)
        return images

    class Meta:
        model = Post
        fields = [
            "id",
            "member",
            "short_body",
            "images",
            "longitude",
            "latitude",
            "total_attention_cnt",
            "total_comment_cnt",
            "is_tabbed",
            "created_on",
        ]


class PostDetailInfoSerializer(serializers.ModelSerializer):
    member = MemberSerializer(read_only=True)
    comments = CommentInfoSerializer(read_only=True, many=True)
    is_tabbed = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    def get_is_tabbed(self, obj: Post):
        member = self.context["request"].user
        if isinstance(member, AnonymousUser):
            return False
        return obj.attentions.filter(member=member, is_deleted=False).exists()

    def get_images(self, obj: Post):
        images = []
        for img in obj.images.all():
            images.append(img.image.url)
        return images

    class Meta:
        model = Post
        fields = [
            "id",
            "member",
            "body",
            "images",
            "longitude",
            "latitude",
            "total_attention_cnt",
            "total_comment_cnt",
            "is_tabbed",
            "comments",
            "created_on",
        ]
