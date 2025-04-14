from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.response import Response

from .serializers import AgentSerializer, ImageCaptionSerializer,ImageGenerationSerializer
from .models import Agent, ImageCaption, ImageGeneration
from utils import image_generator
from django.core.files.base import ContentFile
import time
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

class ImageGenerationViewSet(ModelViewSet):
    """
    API endpoint that allows text to image services to be created, viewed and deleted by authenticated users.
    """

    queryset = ImageGeneration.objects.all()
    serializer_class = ImageGenerationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete"]
    search_fields = ["prompt", "agent__name"]
    filterset_fields = ["agent", "user"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        prompt = request.data.get("prompt")
        agent_id = request.data.get("agent")

        if not prompt or not agent_id:
            return Response({"error": "Prompt and agent are required."}, status=400)

        try:
            agent = Agent.objects.get(id=agent_id)
        except Agent.DoesNotExist:
            return Response({"error": "Agent not found."}, status=404)

        try:
            image_data = image_generator.generate_image_from_prompt(prompt)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        timestamp = time.time()
        image_file = ContentFile(image_data, name="generated_${timestamp}.png")
        instance = ImageGeneration.objects.create(
            prompt=prompt,
            image=image_file,
            agent=agent,
            user=request.user
        )

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=201)
