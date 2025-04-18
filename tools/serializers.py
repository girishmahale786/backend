from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from .models import Agent, ImageCaption, ImageGeneration, PhishingAgent
from .services import (
    ImageCaptionService,
    ImageGenerationService,
    PhishingDetectionService,
)
from django.core.files.base import ContentFile


class AgentSerializer(ModelSerializer):
    class Meta:
        model = Agent
        fields = "__all__"


class ImageCaptionSerializer(ModelSerializer):
    class Meta:
        model = ImageCaption
        fields = "__all__"
        read_only_fields = ["user", "caption"]

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["agent"] = AgentSerializer(instance.agent).data
        return repr

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


class ImageGenerationSerializer(ModelSerializer):
    class Meta:
        model = ImageGeneration
        fields = "__all__"
        read_only_fields = ["user", "image"]

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["agent"] = AgentSerializer(instance.agent).data
        return repr

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        instance = super().create(validated_data)
        agent = instance.agent
        prompt = instance.prompt
        service = ImageGenerationService(agent=agent, prompt=prompt)
        try:
            image_data = service.generate_image()
            timestamp = instance.created_at.strftime("%Y%m%d%H%M%S")
            image = ContentFile(
                image_data, name=f"aiworksuite_generated_image_{timestamp}.jpg"
            )
            instance.image = image
            instance.save()
            return instance
        except Exception as e:
            instance.delete()
            raise ValidationError("Error generating image")


class PhishingDetectionSerializer(ModelSerializer):
    class Meta:
        model = PhishingAgent
        fields = "__all__"
        read_only_fields = ["user", "result"]
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["agent"] = AgentSerializer(instance.agent).data
        return repr

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        instance = super().create(validated_data)
        agent = instance.agent
        url = instance.url
        service = PhishingDetectionService(agent=agent, url=url)
        try:
            result = service.detect_phishing()
            instance.result = result
            instance.save()
            return instance
        except Exception as e:
            instance.delete()
            raise ValidationError("Error detecting phishing")
