
# from django.core.mail import send_mail
# import os
# from dotenv import load_dotenv
import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.settings")

# import django
# django.setup()

# from django.core.management import call_command
from django.conf import settings
# Load environment variables from .env file
# load_dotenv
settings.configure()
# from django.conf import settings
# def send_email(data):
email_user = settings.EMAIL_HOST_USER
email_pass = settings.EMAIL_HOST_PASSWORD
print(email_user, email_pass)
    # email_pass = settings.EMAIL_HOST_PASSWORD
#     send_mail(
#         subject=data["email_subject"],
#         message=data["body"],
#         from_email=email_user,
#         recipient_list=[data["to_email"]],
#         auth_user=email_user,
#         auth_password=email_pass,
# )
