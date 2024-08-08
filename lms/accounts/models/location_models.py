from django.db import models


class City(models.Model):
    """Cities the Programs are being offerend in."""
    city = models.CharField(max_length=50)
    shortname = models.CharField(max_length=3)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


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


class Location(models.Model):
    """Available locations in cities."""
    name = models.CharField(max_length=100)
    shortname = models.CharField(max_length=3)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    capacity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class Sessions(models.Model):
    """Location based sessions."""
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    no_of_students = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
