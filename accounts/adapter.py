from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class AccountAdapter(DefaultAccountAdapter):

    def get_email_confirmation_url(self, request, emailconfirmation):
        url = settings.FRONTEND_CONFIRM_EMAIL_URL
        url = url.replace("{key}", str(emailconfirmation.key))
        return url
