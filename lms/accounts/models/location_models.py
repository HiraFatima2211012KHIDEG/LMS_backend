from django.db import models
# from course.models.program_model import Program

class City(models.Model):
    """Cities the Programs are being offerend in."""
    city = models.CharField(max_length=50)
    shortname = models.CharField(max_length=3)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    def __str__(self):
        return f"{self.city}"

class Batch(models.Model):
    """Batches of cities."""
    batch = models.CharField(max_length=10, primary_key=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    year = models.IntegerField()
    no_of_students = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.batch:
            self.batch = f"{self.city.shortname}-{str(self.year)[-2:]}"
        super(Batch, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('city', 'year')
    def __str__(self):
        return f"{self.batch}"

class Location(models.Model):
    """Available locations in cities."""
    name = models.CharField(max_length=100)
    shortname = models.CharField(max_length=3)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    capacity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.shortname} - {self.city}"

class Sessions(models.Model):
    """Location based sessions."""
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    no_of_students = models.IntegerField()
    is_active = models.BooleanField(default=True)
    program = models.ForeignKey('course.Program', on_delete=models.CASCADE, null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.batch} - {self.location} - {self.no_of_students}"


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