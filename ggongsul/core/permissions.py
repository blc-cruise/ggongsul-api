from rest_framework.permissions import BasePermission, IsAuthenticated


class HasMembershipBenefits(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.has_membership_benefits
        )


class IsObjectOwnerMember(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.member
