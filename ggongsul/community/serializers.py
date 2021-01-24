from typing import Optional

from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ggongsul.community.models import Post, Comment, PostImage
from ggongsul.core.exceptions import BadResponse
from ggongsul.lib.kakao import KakaoApiHelper
from ggongsul.member.serializers import MemberSerializer


def coord_to_region(lng: float, lat: float) -> Optional[str]:
    helper = KakaoApiHelper()

    try:
        res = helper.coord_to_region(lng=lng, lat=lat)
    except BadResponse as e:
        if e.status_code == -2:
            return "부정확한 주소"
        return None

    docs = res.get("documents", [])
    if docs:
        return docs[0]["address_name"]

    return None


class PostSerializer(serializers.ModelSerializer):
    def validate(self, attrs: dict):
        attrs["member"] = self.context["request"].user
        attrs["address"] = coord_to_region(attrs["longitude"], attrs["latitude"])
        return attrs

    class Meta:
        model = Post
        fields = [
            "id",
            "member",
            "address",
            "body",
            "longitude",
            "latitude",
            "images",
        ]
        extra_kwargs = {
            "member": {"required": False, "allow_null": True},
            "address": {"required": False, "allow_null": True},
        }


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
    address = serializers.SerializerMethodField()

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

    def get_address(self, obj: Post):
        if obj.address:
            return obj.address
        if not obj.longitude or not obj.latitude:
            return _("부정확한 주소")

        address = coord_to_region(float(obj.longitude), float(obj.latitude))
        if not address:
            return _("부정확한 주소")

        obj.address = address
        obj.save()
        return obj.address

    class Meta:
        model = Post
        fields = [
            "id",
            "member",
            "short_body",
            "images",
            "address",
            "total_attention_cnt",
            "total_comment_cnt",
            "is_tabbed",
            "created_on",
        ]


class PostDetailInfoSerializer(PostShortInfoSerializer):
    comments = CommentInfoSerializer(read_only=True, many=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "member",
            "body",
            "images",
            "address",
            "total_attention_cnt",
            "total_comment_cnt",
            "is_tabbed",
            "comments",
            "created_on",
        ]
