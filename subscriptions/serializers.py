from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import NotAcceptable
from .models import Plan, Subscription


class PlanSerializer(ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["discounted_price"] = instance.discounted_price
        return repr


class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"
        read_only_fields = ["user"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            if field.startswith("plan_"):
                self.fields[field].read_only = True

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["plan_discounted_price"] = instance.plan_discounted_price
        repr["expiry_date"] = instance.expiry_date
        repr["is_expired"] = instance.is_expired
        return repr

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user

        # Snapshot the plan
        plan = validated_data["plan"]
        for field in plan._meta.fields:
            validated_data[f"plan_{field.name}"] = getattr(plan, field.name)

        subscriptions = self.Meta.model.objects.filter(user=user)
        if subscriptions.exists():
            subscription = subscriptions.latest("updated_at")
            if not subscription.is_expired:
                raise NotAcceptable(
                    {
                        "non_field_errors": f"'{user}' user has already subscribed '{subscription.plan}' subscription"
                    },
                    "invalid_request",
                )

        return super().create(validated_data)
