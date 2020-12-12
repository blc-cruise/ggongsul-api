import logging

from django import forms
from django.core.exceptions import ValidationError
from django.contrib import admin

from ggongsul.lib.kakao import KakaoApiHelper

from .models import Partner, PartnerDetail, PartnerCategory, PartnerAgreement


logger = logging.getLogger(__name__)


class PartnerDetailInline(admin.StackedInline):
    model = PartnerDetail
    exclude = ("secret_token",)


class PartnerAgreementInline(admin.StackedInline):
    model = PartnerAgreement


@admin.register(PartnerCategory)
class PartnerCategoryAdmin(admin.ModelAdmin):
    pass


class PartnerForm(forms.ModelForm):
    def clean_is_active(self):
        is_active = self.cleaned_data.get("is_active")

        if is_active and (
            self.instance.latitude is None or self.instance.longitude is None
        ):
            raise ValidationError("주소 정보가 정확하지 않은것 같습니다! 한번더 확인해주세요.")

        return is_active

    def save(self, commit=True):
        helper = KakaoApiHelper()

        res: dict = helper.search_address(self.instance.address)
        logger.debug(res)

        # 정확히 주소가 맞을때만 입력
        if len(res.get("documents", [])) == 1:
            doc: dict = res["documents"][0]
            self.instance.longitude = doc.get("x", None)
            self.instance.latitude = doc.get("y", None)

        return super().save(commit)

    class Meta:
        model = Partner
        fields = "__all__"


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    form = PartnerForm
    inlines = [PartnerAgreementInline, PartnerDetailInline]
    exclude = ("longitude", "latitude")
    list_display = (
        "name",
        "address",
        "contact_name",
        "detail_update_url",
        "policy_agree_yn",
        "is_active",
    )
