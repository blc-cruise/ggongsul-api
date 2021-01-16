from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ggongsul.partner import views as partner_views
from ggongsul.agreement import views as agreement_views
from ggongsul.review import views as review_views
from ggongsul.visitation import views as visitation_views
from ggongsul.member import views as member_views
from ggongsul.membership import views as membership_views
from ggongsul.community import views as community_views


v1_router = DefaultRouter()
v1_router.register("partners", partner_views.PartnerViewSet)
v1_router.register("agreements", agreement_views.AgreementViewSet)
v1_router.register("reviews", review_views.ReviewViewSet)
v1_router.register("visitations", visitation_views.VisitationViewSet)
v1_router.register("members", member_views.MemberViewSet)
v1_router.register("memberships", membership_views.MembershipViewSet)
v1_router.register("posts", community_views.PostViewSet)
v1_router.register(r"posts/(?P<post_id>\d+)/comments", community_views.CommentViewSet)


urlpatterns = [
    path("v1/", include(v1_router.urls)),
]
