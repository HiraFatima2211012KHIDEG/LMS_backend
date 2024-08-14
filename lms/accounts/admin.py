from django.contrib import admin
from django.contrib.auth import get_user_model
from .models.models_ import Applications, AccessControl, Student, Sessions, City, Location, Batch


class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'contact', 'city']


admin.site.register(get_user_model(), UserAdmin)
admin.site.register(Applications)
admin.site.register(AccessControl)
admin.site.register(Student)
admin.site.register(Sessions)
admin.site.register(City)
admin.site.register(Batch)
admin.site.register(Location)




