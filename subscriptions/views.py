from .serializers import PlanSerializer, SubscriptionSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from .models import Plan, Subscription


# Create your views here.


class PlanViewSet(ModelViewSet):
    """
    API endpoint that allows subscription plans to be viewed.
    """

    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ["get"]
    search_fields = ["name"]


class SubscriptionViewSet(ModelViewSet):
    """
    API endpoint that allows subscriptions to be created and viewed by authenticated users.
    """

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post"]
    filterset_fields = ["user"]
    search_fields = ["plan", "user"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
