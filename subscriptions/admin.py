from django.contrib import admin
from .models import Plan, Subscription

# Register your models here.


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "price", "discounted_price", "duration"]
    list_display_links = ["id", "name", "price", "discounted_price", "duration"]
    readonly_fields = ["discounted_price"]
    search_fields = ["id", "name"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "plan",
        "plan_price",
        "plan_discounted_price",
        "expiry_date",
        "is_expired",
    ]
    list_display_links = [
        "id",
        "user",
        "plan",
        "plan_price",
        "plan_discounted_price",
        "expiry_date",
        "is_expired",
    ]
    readonly_fields = [
        "plan",
        "plan_name",
        "plan_duration",
        "plan_price",
        "plan_discount",
        "plan_discounted_price",
        "expiry_date",
        "is_expired",
        "created_at",
        "updated_at",
    ]
    raw_id_fields = ["plan", "user"]
    search_fields = [
        "id",
        "user__id",
        "plan__id",
        "plan__name",
    ]
