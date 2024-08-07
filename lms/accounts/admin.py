from django.contrib import admin
from django.contrib.auth import get_user_model
from .models.user_models import Applications, AccessControl, StudentInstructor
from .models.location_models import City,Location, Sessions, Batch


class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'contact', 'city']


admin.site.register(get_user_model(), UserAdmin)
admin.site.register(Applications)
admin.site.register(AccessControl)
admin.site.register(StudentInstructor)
admin.site.register(City)
admin.site.register(Location)
admin.site.register(Sessions)
admin.site.register(Batch)