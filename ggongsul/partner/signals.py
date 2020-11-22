from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Partner, PartnerDetail


@receiver(post_save, sender=Partner)
def create_profile(sender, instance, created, **kwargs):
    if created:
        PartnerDetail.objects.create(partner=instance)
