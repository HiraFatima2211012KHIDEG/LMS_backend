from django.urls import reverse
from rest_framework import status
from ..models.location_models import Sessions, Location, Batch, City
from .test_location_views import BaseAPITestCase
from ..models.user_models import Applications, StudentInstructor
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


CREATE_URL = reverse("attendance-list-create")


class AttendanceTestCases(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        city = City.objects.create(city="Karachi", shortname="KHI")
        location = Location.objects.create(
            name="Malir", shortname="MLR", city=city, capacity=20
        )
        batch = Batch.objects.create(
            city=city,
            year=2024,
            no_of_students=1000,
            start_date="2024-01-01",
            end_date="2024-12-31",
        )
        self.session = Sessions.objects.create(
            batch=batch, location=location, no_of_students=100
        )
        Group.objects.create(name="student")
        Applications.objects.create(email="student@example.com", group_name="student")
        self.student = get_user_model().objects.create_user(
            email="student@example.com",
            password="TestPass&123",
        )
        self.user_registration = StudentInstructor.objects.create(user_id=self.user.id, batch=batch)
        self.student_registration = StudentInstructor.objects.create(user_id=self.student.id, batch=batch)
        self.client.force_authenticate(user=self.student)

    def test_create_attendance(self):
        """Test creating attendance successfully"""
        payload = {
            "session": self.session.id,
            "marked_by": self.user_registration.registration_id,
            "status": "Present",
            "student": self.student_registration.registration_id,
        }
        res = self.client.post(CREATE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["data"]["session"], payload["session"])

    def test_retrieve_attendance(self):
        """test retrieving attendance."""
        payload = {
            "session": self.session.id,
            "marked_by": self.user_registration.registration_id,
            "status": "Present",
            "student": self.student_registration.registration_id,
        }
        self.client.post(CREATE_URL, payload)
        res = self.client.get(CREATE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
