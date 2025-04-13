from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from .models import Agent, ImageCaption
from .services import ImageCaptionService

class AgentSerializer(ModelSerializer):
    class Meta:
        model = Agent
        fields = "__all__"


class ImageCaptionSerializer(ModelSerializer):
    class Meta:
        model = ImageCaption
        fields = "__all__"
        read_only_fields = ["user", "caption"]
    
    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        instance = super().create(validated_data)
        agent = instance.agent
        image = instance.image
        service = ImageCaptionService(agent=agent, image_path=image)
        try:
            caption = service.generate_caption()
            instance.caption = caption
            instance.save()
            return instance
        except Exception as e:
            instance.delete()
            raise ValidationError("Error generating caption")
