import re
import threading
from rest_framework.exceptions import ValidationError
from django.template.loader import render_to_string
from users.models import AuthType
from django.core.mail import EmailMessage

email_regex = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}")
phone_regex = re.compile(r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$")


def check_email_or_phone(email_or_phone):

    if email_regex.fullmatch(email_or_phone):
        return AuthType.VIA_EMAIL
    elif phone_regex.fullmatch(email_or_phone):
        return AuthType.VIA_PHONE

    data = {
        "success": False,
        "message": "Emailingi yoki Telefonn raqamingiz natogri yuborilgan ",
    }

    raise ValidationError(data)


class EmailThread(threading.Thread):

    def __init__(self, email):
        super().__init__()
        self.email = email

    def run(self):
        return self.email.send()


class Email:
    @staticmethod
    def send_email(data):

        email = EmailMessage(
            subject=data["subject"],
            body=data["body"],
            to=[data["email_to"]],
        )

        if data["content_type"] == "html":
            email.content_subtype = "html"
        EmailThread(email).start()


def send_email(to_email, code):
    html_content = render_to_string(
        "email/authenticated/activate_user.html", {"code": code}
    )
    
    Email.send_email({
        'subject' : 'Tastiqlsh kodi',
        'body' : html_content ,
        'content_type' : 'html',
        'email_to' : to_email
    })
