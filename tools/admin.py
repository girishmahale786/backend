from django.contrib import admin
from .models import Agent, ImageCaption

# Register your models here.

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "tool"]
    list_display_links = list_display
    list_filter = ["tool"]
    readonly_fields = ["created_at", "updated_at"]
    search_fields = ["id", "title"]


@admin.register(ImageCaption)
class ImageCaptionAdmin(admin.ModelAdmin):
    list_display = ["id", "agent", "user", "caption"]
    list_display_links = list_display
    readonly_fields = ["created_at", "updated_at"]
    search_fields = ["id", "agent__name", "user__email", "caption"]
