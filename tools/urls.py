from django.urls import path, include

from rest_framework import routers
from .views import AgentViewSet, ImageCaptionViewSet, PhishingDetectionViewSet

router = routers.DefaultRouter()
router.register("agents", AgentViewSet)
router.register("image-captions", ImageCaptionViewSet)
router.register("phishing-detections", PhishingDetectionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
