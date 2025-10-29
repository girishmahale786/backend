from django.urls import path, include

from rest_framework import routers
from .views import AgentViewSet, ImageCaptionViewSet, ImageGenerationViewSet, PhishingDetectionViewSet, MemoryJournalView

router = routers.DefaultRouter()
router.register("agents", AgentViewSet)
router.register("image-captions", ImageCaptionViewSet)
router.register("image-generations", ImageGenerationViewSet)
router.register("phishing-detections", PhishingDetectionViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("memory-journal/", MemoryJournalView.as_view(), name="memory-journal"),
]
