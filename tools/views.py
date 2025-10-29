from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, status

from .serializers import (
    AgentSerializer,
    ImageCaptionSerializer,
    ImageGenerationSerializer,
    PhishingDetectionSerializer,
)
from .models import Agent, ImageCaption, ImageGeneration, PhishingAgent

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from utils.memory_journal import MemoryJournal
import tempfile
import os


# Create your views here.

mj = MemoryJournal()

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
    API endpoint that allows image generations to be created, viewed and deleted by authenticated users.
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


class PhishingDetectionViewSet(ModelViewSet):
    """
    API endpoint that allows phishing detections to be created, viewed and deleted by authenticated users.
    """

    queryset = PhishingAgent.objects.all()
    serializer_class = PhishingDetectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete"]
    search_fields = ["url", "agent__name"]
    filterset_fields = ["agent", "user"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class MemoryJournalView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        audio_file = request.FILES.get("audio")
        video_file = request.FILES.get("video")
        print("Received files:", audio_file, video_file)

        if not audio_file or not video_file:
            return Response({"error": "Both audio and video are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # ------------------- Audio -------------------
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio.write(audio_file.read())
                temp_audio.flush()
                # from pydub import AudioSegment
                # audio_segment = AudioSegment.from_file(temp_audio.name)
                # audio_segment.export(temp_audio.name, format="wav")

                print("Transcribing audio...", temp_audio.name)
                audio_transcript = mj.transcribe(temp_audio.name)
                print("Transcription:", audio_transcript)

            os.remove(temp_audio.name)

            # ------------------- Video -------------------
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
                temp_video.write(video_file.read())
                temp_video.flush()
                print("Generating video caption...", temp_video.name)
                video_caption = mj.video_caption(temp_video.name)
                print("Video caption:", video_caption)
            
            os.remove(temp_video.name)

            # ------------------- Summary -------------------
            summary = mj.text_summary(video_caption, audio_transcript)

            return Response({
                "video_caption": video_caption,
                "audio_transcript": audio_transcript,
                "summary": summary
            })

        except Exception as e:
            print("Error processing files:", str(e))
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
