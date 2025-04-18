from django.db import models
from accounts.models import User

# Create your models here.


TOOLS = (
    ("image-captioning", "Image Captioning"),
    ("image-generation", "Image Generation"),
    ("phishing-detection", "Phishing Detection"),
    ("other", "Other"),
)


class Agent(models.Model):
    name = models.CharField(max_length=255)
    tool = models.CharField(max_length=255, choices=TOOLS, default='other')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class ImageCaption(models.Model):
    image = models.ImageField(upload_to='images/')
    caption = models.TextField()
    agent = models.ForeignKey(Agent, on_delete=models.RESTRICT, related_name='captions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='captions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.caption[:50]

    class Meta:
        ordering = ['-created_at']


class ImageGeneration(models.Model): 
    image = models.ImageField(upload_to='images/')
    prompt = models.TextField()
    agent = models.ForeignKey(Agent, on_delete=models.RESTRICT, related_name="image_generations")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="image_generations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.prompt[:50]
    
    class Meta:
        ordering = ['-created_at']


class PhishingAgent(models.Model):
    url = models.URLField()
    result = models.FloatField(null=True)
    agent = models.ForeignKey(Agent, on_delete=models.RESTRICT, related_name="phishing_agents")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="phishing_agents")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
