import re
from rest_framework.exceptions import ValidationError

email_regex = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}")
phone_regex = re.compile(r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$")


def check_email_or_phone(email_or_phone):
    if email_regex.fullmatch(email_or_phone):
        return "email"
    elif phone_regex.fullmatch(email_or_phone):
        return "phone"

    data = {
        "success": False,
        "message": "Emailingi yoki Telefonn raqamingiz natogri yuborilgan ",
    }

    raise ValidationError(data)
