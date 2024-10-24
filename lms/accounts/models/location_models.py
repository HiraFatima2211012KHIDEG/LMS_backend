from django.db import models

from constants import STATUS_CHOICES, ROOMS, WEEKDAYS, TERM_CHOICES
from django.utils import timezone


# class City(models.Model):
#     """Cities the Programs are being offerend in."""

#     city = models.CharField(max_length=50)
#     shortname = models.CharField(max_length=3)
#     is_active = models.BooleanField(default=True)
#     status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
#     created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
#     updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

#     def __str__(self):
#         return f"{self.city}"


class Batch(models.Model):
    """Batches of cities."""

    name = models.CharField(max_length=50, null=True)
    batch = models.CharField(max_length=10, primary_key=True)
    short_name = models.CharField(max_length=5, null=True)

    # city = models.CharField(max_length=30)
    # city_abb = models.CharField(max_length=3)
    year = models.IntegerField()
    no_of_students = models.IntegerField()
    application_start_date = models.DateField(null=True)
    application_end_date = models.DateField(null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    # term = models.CharField(max_length=10, choices=TERM_CHOICES, null=True, blank=True)

    def save(self, *args, **kwargs):
        # if not self.term:
        #     current_month = (
        #         timezone.now().month
        #     )
        #     if current_month in [9, 10, 11]:
        #         self.term = "Fall"
        #     elif current_month in [12, 1, 2]:
        #         self.term = "Winter"
        #     elif current_month in [3, 4, 5]:
        #         self.term = "Spring"
        #     elif current_month in [6, 7, 8]:
        #         self.term = "Summer"
        #     else:
        #         self.term = "Annual"

        if not self.batch:
            self.batch = f"{self.short_name.upper()}-{str(self.year)[-2:]}"
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("short_name", "year")

    def __str__(self):
        return f"{self.batch}"


# class Location(models.Model):
#     """Available locations in cities."""

#     name = models.CharField(max_length=100)
#     shortname = models.CharField(max_length=3)
#     city = models.CharField(max_length=30, null=True)
#     capacity = models.IntegerField()
#     status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
#     created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
#     updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

#     def __str__(self):
#         return f"{self.name} - {self.shortname} - {self.city}"


class Sessions(models.Model):
    """Location-based sessions."""

    location = models.PositiveSmallIntegerField(choices=ROOMS, null=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True)
    no_of_students = models.IntegerField()
    course = models.ForeignKey("course.Course", on_delete=models.CASCADE, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    days_of_week = models.JSONField(default=list, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = ("batch", "location", "course", "start_date", "end_date")

    def __str__(self):
        return f"{self.location} - {self.course} - {self.no_of_students}"


class SessionSchedule(models.Model):
    """Schedule for a session on a specific day."""

    session = models.ForeignKey(
        Sessions, on_delete=models.CASCADE, related_name="schedules"
    )
    day_of_week = models.CharField(
        max_length=10,
        choices=[
            ("Monday", "Monday"),
            ("Tuesday", "Tuesday"),
            ("Wednesday", "Wednesday"),
            ("Thursday", "Thursday"),
            ("Friday", "Friday"),
            ("Saturday", "Saturday"),
            ("Sunday", "Sunday"),
        ],
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ("session", "day_of_week")

    def __str__(self):
        return (
            f"{self.session} - {self.day_of_week}: {self.start_time} - {self.end_time}"
        )
