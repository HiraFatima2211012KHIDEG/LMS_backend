from django.db import models

from utils.custom import STATUS_CHOICES
from datetime import timedelta
from django.utils import timezone


class City(models.Model):
    """Cities the Programs are being offerend in."""

    city = models.CharField(max_length=50)
    shortname = models.CharField(max_length=3)
    is_active = models.BooleanField(default=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.city}"


class Batch(models.Model):
    """Batches of cities."""

    batch = models.CharField(max_length=10, primary_key=True)
    city = models.CharField(max_length=30)
    city_abb = models.CharField(max_length=3)
    year = models.IntegerField()
    no_of_students = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    TERM_CHOICES = [
        ("Fall", "Fall"),
        ("Winter", "Winter"),
        ("Spring", "Spring"),
        ("Summer", "Summer"),
        ("Annual", "Annual"),
    ]
    term = models.CharField(max_length=10, choices=TERM_CHOICES, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Assign the term based on the current month if term is not provided
        if not self.term:
            current_month = (
                timezone.now().month
            )  # This should now use Django's timezone correctly
            if current_month in [9, 10, 11]:
                self.term = "Fall"
            elif current_month in [12, 1, 2]:
                self.term = "Winter"
            elif current_month in [3, 4, 5]:
                self.term = "Spring"
            elif current_month in [6, 7, 8]:
                self.term = "Summer"
            else:
                self.term = "Annual"

        # Generate the batch code if not provided
        if not self.batch:
            self.batch = (
                f"{self.city_abb.upper()}-{self.term[:2]}-{str(self.year)[-2:]}"
            )

        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("city", "year", "term")

    def __str__(self):
        return f"{self.batch}"


class Location(models.Model):
    """Available locations in cities."""

    name = models.CharField(max_length=100)
    shortname = models.CharField(max_length=3)
    city = models.CharField(max_length=30, null=True)
    capacity = models.IntegerField()
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.shortname} - {self.city}"


WEEKDAYS = {
    0: ("Monday", "Mon"),
    1: ("Tuesday", "Tue"),
    2: ("Wednesday", "Wed"),
    3: ("Thursday", "Thu"),
    4: ("Friday", "Fri"),
    5: ("Saturday", "Sat"),
    6: ("Sunday", "Sun"),
}


class Sessions(models.Model):
    """Location-based sessions."""
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    no_of_students = models.IntegerField()
    # batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    course = models.ForeignKey("course.Course", on_delete=models.CASCADE, null=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    days_of_week = models.JSONField(default=list, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        unique_together = ("location", "start_time", "end_time", "course")

    def __str__(self):
        return f"{self.location}-{self.course}-{self.no_of_students}-{self.start_time}-{self.end_time}"


# class Batch(models.Model):
#     """Batches of cities."""
#     batch = models.CharField(max_length=10, primary_key=True)
#     city = models.ForeignKey(City, on_delete=models.CASCADE)
#     year = models.IntegerField()
#     no_of_students = models.IntegerField()
#     start_date = models.DateField()
#     end_date = models.DateField()
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

#     # term_choices = [
#     #     ('Fall', 'fall'),
#     #     ('Winter', 'winter'),
#     #     ('Spring', 'spring'),
#     #     ('Summer', 'summer'),
#     #     ('Annual', 'annual')
#     # ]
#     # term = models.CharField(max_length=10, choices=term_choices)

#     def save(self, *args, **kwargs):
#         # Generate the batch code if not provided
#         if not self.batch:
#             self.batch = f"{self.city.shortname}-{str(self.year)[-2:]}"

#         # # Assign the term based on the created_at month if term is not provided
#         # if not self.term:
#         #     if self.created_at and self.created_at.month in [9, 10, 11]:
#         #         self.term = 'fall'
#         #     elif self.created_at and self.created_at.month in [12, 1, 2]:
#         #         self.term = 'winter'
#         #     elif self.created_at and self.created_at.month in [3, 4, 5]:
#         #         self.term = 'spring'
#         #     elif self.created_at and self.created_at.month in [6, 7, 8]:
#         #         self.term = 'summer'
#         #     else:
#         #         self.term = 'annual'  # Default if no match

#         super(Batch, self).save(*args, **kwargs)

#     class Meta:
#         unique_together = ('city', 'year')
