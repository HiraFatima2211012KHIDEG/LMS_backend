from django.core.mail import send_mail
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.settings")
django.setup()

send_mail(
    subject="Test Email",
    message="This is a test email.",
    from_email="maazjavaidsiddique10@gmail.com",
    recipient_list=["hira.fatima@xloopdigital.com"],
    fail_silently=False,
)
# send_mail()
