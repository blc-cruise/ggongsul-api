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
    can_delete = False
    readonly_fields = ("created_on", "updated_on")


class PartnerAgreementInline(admin.TabularInline):
    model = PartnerAgreement
    can_delete = False
    readonly_fields = ("policy_agreed_at", "created_on", "updated_on")


@admin.register(PartnerCategory)
class PartnerCategoryAdmin(admin.ModelAdmin):
    pass


class PartnerForm(forms.ModelForm):
    def clean_cert_num(self):
        cert_num = self.cleaned_data.get("cert_num")
        if cert_num and not cert_num.isdigit():
            raise ValidationError("인증 번호는 반드시 숫자만 포함해야합니다!")
        return cert_num

    def clean_is_active(self):
        is_active = self.cleaned_data.get("is_active")

        if is_active and (
            self.instance.latitude is None or self.instance.longitude is None
        ):
            raise ValidationError("주소 정보가 정확하지 않은것 같습니다! 한번더 확인해주세요.")

        if is_active and self.instance.cert_num is None:
            raise ValidationError("업체 인증 번호가 설정되지 않았습니다! 인증 번호를 설정 후 활성화 해주세요.")

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
    list_filter = ("is_active",)
    search_fields = ("name", "contact_name")
    list_display = (
        "name",
        "id",
        "address",
        "contact_name",
        "detail_update_url",
        "policy_agree_yn",
        "is_active",
    )

    # 등록된 파트 정보는 admin에서 삭제할 수 없도록 처리
    def has_delete_permission(self, request, obj=None):
        return False
