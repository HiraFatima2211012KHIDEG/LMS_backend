from django.core.mail import send_mail
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def send_email(data):
    email_user = os.getenv("EMAIL_HOST_USER")
    email_pass = os.getenv("EMAIL_HOST_PASSWORD")
    # print(email_user, email_pass)
    # email_pass = settings.EMAIL_HOST_PASSWORD
    send_mail(
        subject=data["email_subject"],
        message=data["body"],
        from_email=email_user,
        recipient_list=[data["to_email"]],
        auth_user=email_user,
        auth_password=email_pass,
    )
