from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions

from .serializers import AgentSerializer, ImageCaptionSerializer
from .models import Agent, ImageCaption

# Create your views here.


class AgentViewSet(ModelViewSet):
    """
    API endpoint that allows agents to be viewed by users.
    """

    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ["get"]
    search_fields = ["name", "tool"]
    filterset_fields = ["tool"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-updated_at"]


class ImageCaptionViewSet(ModelViewSet):
    """
    API endpoint that allows image captions to be created, viewed and deleted by authenticated users.
    """

    queryset = ImageCaption.objects.all()
    serializer_class = ImageCaptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete"]
    search_fields = ["caption", "agent__name"]
    filterset_fields = ["agent", "user"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
