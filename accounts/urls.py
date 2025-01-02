from django.urls import path, include
from allauth.socialaccount import urls
from .views import GoogleLogin

urlpatterns = [
    path("", include("dj_rest_auth.urls")),
    path("register/", include("dj_rest_auth.registration.urls")),
    path("auth/", include("allauth.urls")),
    path("google_login/", GoogleLogin.as_view(), name="google_login"),
]
