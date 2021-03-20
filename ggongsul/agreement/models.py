from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField


class Agreement(models.Model):
    name = models.CharField(max_length=32, verbose_name=_("약관 이름"))
    body = RichTextField(blank=True, verbose_name=_("약관 본문"))

    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("생성 날짜"))
    updated_on = models.DateTimeField(auto_now=True, verbose_name=_("최근 정보 변경 날짜"))

    class Meta:
        verbose_name = _("이용 약관")
        verbose_name_plural = _("이용 약관")

    def __str__(self):
        return self.name
