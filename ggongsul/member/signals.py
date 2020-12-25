from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Member, MemberDetail, MemberAgreement


@receiver(post_save, sender=Member)
def create_profile(sender, instance, created, **kwargs):
    if created:
        MemberDetail.objects.create(member=instance)
        MemberAgreement.objects.create(member=instance)
