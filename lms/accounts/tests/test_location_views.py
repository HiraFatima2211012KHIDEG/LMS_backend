from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from ..models.models_ import City, Applications, Batch, Location, Sessions
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


CITY_CREATE_LIST_URL = reverse('city-list-create')

def detail_city_url(city_id):
    """Create and return the detail url of city."""
    return reverse('city-detail', args=[city_id])

def create_user(email='user@example.com', password='TestPass&123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)

def create_application(email, group_name):
        """Create and return new application"""
        return Applications.objects.create(email=email, group_name=group_name)

class BaseAPITestCase(TestCase):
    """Base setup for all API Test cases"""

    def setUp(self):
        Group.objects.create(name='instructor')
        Applications.objects.create(email='instructor@example.com', group_name='instructor')
        self.user = create_user(
            email = 'instructor@example.com',
            password = 'TestPass&123',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

class CityAPITests(BaseAPITestCase):
    """Test authenticated API requests for City APIs"""
    def setUp(self):
        super().setUp()

    def test_create_city(self):
        paylod = {
            'city': 'Karachi',
            'shortname': 'KHI'
        }
        response = self.client.post(CITY_CREATE_LIST_URL, paylod)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'created successfully')

    def test_list_cities(self):
        City.objects.create(city='Karachi', shortname='KHI')
        response = self.client.get(CITY_CREATE_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), City.objects.count())

    def test_retrieve_city(self):
        city = City.objects.create(city='Karachi', shortname='KHI')
        url = detail_city_url(city.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['city'], city.city)
        self.assertEqual(response.data['shortname'], city.shortname)

    def test_update_city(self):
        city = City.objects.create(city='Karachi', shortname='KHI')
        url = detail_city_url(city.id)
        payload = {'city': 'Updated City', 'shortname': 'UPC'}
        response = self.client.put(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        city.refresh_from_db()
        self.assertEqual(city.city, 'Updated City')

    def test_delete_city(self):
        city = City.objects.create(city='Karachi', shortname='KHI')
        url = detail_city_url(city.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(City.objects.filter(id=city.id).exists())



class BatchAPITestCase(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.city = City.objects.create(city='Lahore', shortname='LHR')
        self.batch_data = {
            'city': self.city.id,
            'year': 2024,
            'no_of_students': 30,
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        }
        self.batch = Batch.objects.create(city=self.city, year=2025, no_of_students=30, start_date='2024-01-01', end_date='2024-12-31')
        self.batch_url = reverse('batch-list-create')
        self.batch_detail_url = reverse('batch-detail', args=[self.batch.batch])

    def test_create_batch(self):
        response = self.client.post(self.batch_url, self.batch_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_batches(self):
        response = self.client.get(self.batch_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Batch.objects.count())

    def test_retrieve_batch(self):
        response = self.client.get(self.batch_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['batch'], self.batch.batch)

    def test_update_batch(self):
        updated_data = {
            'city': self.city.id,
            'year': 2025,
            'no_of_students': 40,
            'start_date': '2025-01-01',
            'end_date': '2025-12-31'
        }
        response = self.client.put(self.batch_detail_url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.year, 2025)

    def test_delete_batch(self):
        response = self.client.delete(self.batch_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Batch.objects.filter(batch=self.batch.batch).exists())


class LocationAPITestCase(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.city = City.objects.create(city='Islamabad', shortname='ISB')
        self.location_data = {
            'name': 'Main Campus',
            'shortname': 'MCP',
            'city': self.city.id,
            'capacity': 50
        }
        self.location = Location.objects.create(name='Main Campus', shortname='MCP', city=self.city, capacity=50)
        self.location_url = reverse('location-list-create')
        self.location_detail_url = reverse('location-detail', args=[self.location.id])

    def test_create_location(self):
        response = self.client.post(self.location_url, self.location_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_locations(self):
        response = self.client.get(self.location_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Location.objects.count())

    def test_retrieve_location(self):
        response = self.client.get(self.location_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.location.id)

    def test_update_location(self):
        updated_data = {
            'name': 'Updated Location',
            'shortname': 'ULC',
            'city': self.city.id,
            'capacity': 60
        }
        response = self.client.put(self.location_detail_url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.location.refresh_from_db()
        self.assertEqual(self.location.name, 'Updated Location')

    def test_delete_location(self):
        response = self.client.delete(self.location_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Location.objects.filter(id=self.location.id).exists())


class SessionsAPITestCase(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.city = City.objects.create(city='Quetta', shortname='QTA')
        self.batch = Batch.objects.create(city=self.city, year=2024, no_of_students=30, start_date='2024-01-01', end_date='2024-12-31')
        self.location = Location.objects.create(name='Central Park', shortname='CPK', city=self.city, capacity=100)
        self.session_data = {
            'location': self.location.id,
            'no_of_students': 30,
            'batch': self.batch.batch,
            'start_time': '2024-01-01T09:00:00Z',
            'end_time': '2024-01-01T12:00:00Z'
        }
        self.session = Sessions.objects.create(location=self.location, no_of_students=30, batch=self.batch, start_time='2024-01-01T09:00:00Z', end_time='2024-01-01T12:00:00Z')
        self.session_url = reverse('session-list-create')
        self.session_detail_url = reverse('session-detail', args=[self.session.id])

    def test_create_session(self):
        response = self.client.post(self.session_url, self.session_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_sessions(self):
        response = self.client.get(self.session_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Sessions.objects.count())

    def test_retrieve_session(self):
        response = self.client.get(self.session_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.session.id)

    def test_update_session(self):
        updated_data = {
            'location': self.location.id,
            'no_of_students': 40,
            'batch': self.batch.batch,
            'start_time': '2024-01-01T10:00:00Z',
            'end_time': '2024-01-01T13:00:00Z'
        }
        response = self.client.put(self.session_detail_url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.session.refresh_from_db()
        self.assertEqual(self.session.no_of_students, 40)

    def test_delete_session(self):
        response = self.client.delete(self.session_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Sessions.objects.filter(id=self.session.id).exists())