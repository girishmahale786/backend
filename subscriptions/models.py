from django.db import models
from django.utils import timezone
from accounts.models import User

# Create your models here.


class Plan(models.Model):
    name = models.CharField("name", max_length=255)
    duration = models.DurationField("duration")
    price = models.IntegerField("price", default=0)
    discount = models.SmallIntegerField("discount percentage", default=0)

    def __str__(self):
        return self.name

    @property
    def discounted_price(self):
        discount = self.price * (self.discount / 100)
        return round(self.price - discount)


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    plan_name = models.CharField("name", max_length=255)
    plan_duration = models.DurationField("duration")
    plan_price = models.IntegerField("price", default=0)
    plan_discount = models.SmallIntegerField("discount percentage", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.plan_name

    @property
    def plan_discounted_price(self):
        discount = self.plan_price * (self.plan_discount / 100)
        return round(self.plan_price - discount)

    @property
    def expiry_date(self):
        return self.created_at + self.plan_duration

    @property
    def is_expired(self):
        return timezone.now() > self.expiry_date
