import os
import django
from django.conf import settings

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.settings")

# Initialize Django
django.setup()

from django.contrib.auth import get_user_model

# Now you can run your Django code
User = get_user_model()
user = User.objects.get(id=10002)
# user.soft_delete()
user.set_status(0)
