from django.db import models

from django.utils.translation import gettext_lazy as _

from ggongsul.member.models import Member
from ggongsul.partner.models import Partner


class Visitation(models.Model):
    partner = models.ForeignKey(
        Partner,
        related_name="visitations",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("업체"),
    )
    member = models.ForeignKey(
        Member,
        related_name="visitations",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("사용자"),
    )

    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("생성 날짜"))
    updated_on = models.DateTimeField(auto_now=True, verbose_name=_("최근 정보 변경 날짜"))

    def is_reviewed(self) -> bool:
        if hasattr(self, "review") and self.review is not None:
            return True
        return False

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.member} 의 {self.partner} 방문 기록 {self.id}"

    class Meta:
        ordering = ["-created_on"]
        verbose_name = _("방문 기록")
        verbose_name_plural = _("방문 기록")
