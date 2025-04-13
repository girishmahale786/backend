from django.urls import path, include

from rest_framework import routers
from .views import AgentViewSet, ImageCaptionViewSet

router = routers.DefaultRouter()
router.register("agents", AgentViewSet)
router.register("image-captions", ImageCaptionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
