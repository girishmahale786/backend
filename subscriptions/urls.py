from django.urls import path, include

from rest_framework import routers
from .views import PlanViewSet, SubscriptionViewSet

router = routers.DefaultRouter()
router.register("plans", PlanViewSet)
router.register("", SubscriptionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
