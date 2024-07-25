from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from course.models.models import Program, Course, Module
from course.serializers import ProgramSerializer, CourseSerializer, ModuleSerializer

class ProgramAPITests(APITestCase):
    
    def setUp(self):
        self.program1 = Program.objects.create(
            name='Program 1',
            short_name='P1',
            description='Description for Program 1',
            created_by='Admin'
        )
        self.program2 = Program.objects.create(
            name='Program 2',
            short_name='P2',
            description='Description for Program 2',
            created_by='Admin'
        )
        self.list_create_url = reverse('program-list-create')
        self.detail_url = lambda pk: reverse('program-detail', args=[pk])
    
    def test_list_programs(self):
        response = self.client.get(self.list_create_url)
        programs = Program.objects.all()
        serializer = ProgramSerializer(programs, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response'], serializer.data)
    
    def test_create_program(self):
        data = {
            'name': 'Program 3',
            'short_name': 'P3',
            'description': 'Description for Program 3',
            'created_by': 'Admin',
            'is_active': True  # Ensure this matches your model's field name and type
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['response']['name'], 'Program 3')
    
    def test_retrieve_program(self):
        response = self.client.get(self.detail_url(self.program1.pk))
        serializer = ProgramSerializer(self.program1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response'], serializer.data)
    
    def test_update_program(self):
        data = {
            'name': 'Updated Program 1',
            'short_name': 'UP1',
            'description': 'Updated description',
            'created_by': 'Admin'
        }
        response = self.client.put(self.detail_url(self.program1.pk), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response']['name'], 'Updated Program 1')
    
    def test_delete_program(self):
        response = self.client.delete(self.detail_url(self.program2.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Program.objects.filter(pk=self.program2.pk).exists())

class CourseAPITests(APITestCase):
    
    def setUp(self):
        self.program = Program.objects.create(
            name='Program for Courses',
            short_name='PFC',
            description='Description for Program for Courses',
            created_by='Admin'
        )
        self.course1 = Course.objects.create(
            program=self.program,
            name='Course 1',
            description='Description for Course 1',
            created_by='Admin',
            credit_hours=4
        )
        self.course2 = Course.objects.create(
            program=self.program,
            name='Course 2',
            description='Description for Course 2',
            created_by='Admin',
            credit_hours=3
        )
        self.list_create_url = reverse('course-list-create')
        self.detail_url = lambda pk: reverse('course-detail', args=[pk])
    
    def test_list_courses(self):
        response = self.client.get(self.list_create_url)
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response'], serializer.data)
    
    def test_create_course(self):
        data = {
            'program': self.program.pk,
            'name': 'Course 3',
            'description': 'Description for Course 3',
            'created_by': 'Admin',
            'credit_hours': 5
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['response']['name'], 'Course 3')
    
    def test_retrieve_course(self):
        response = self.client.get(self.detail_url(self.course1.pk))
        serializer = CourseSerializer(self.course1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response'], serializer.data)
    
    def test_update_course(self):
        data = {
            'program': self.program.pk,
            'name': 'Updated Course 1',
            'description': 'Updated description',
            'created_by': 'Admin',
            'credit_hours': 6
        }
        response = self.client.put(self.detail_url(self.course1.pk), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response']['name'], 'Updated Course 1')
    
    def test_delete_course(self):
        response = self.client.delete(self.detail_url(self.course2.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(pk=self.course2.pk).exists())

class ModuleAPITests(APITestCase):
    
    def setUp(self):
        self.program = Program.objects.create(
            name='Program for Modules',
            short_name='PFM',
            description='Description for Program for Modules',
            created_by='Admin'
        )
        self.course = Course.objects.create(
            program=self.program,
            name='Course for Modules',
            description='Description for Course for Modules',
            created_by='Admin',
            credit_hours=4
        )
        self.module1 = Module.objects.create(
            course=self.course,
            name='Module 1',
            description='Description for Module 1',
            created_by='Admin'
        )
        self.module2 = Module.objects.create(
            course=self.course,
            name='Module 2',
            description='Description for Module 2',
            created_by='Admin'
        )
        self.list_create_url = reverse('module-list-create')
        self.detail_url = lambda pk: reverse('module-detail', args=[pk])
    
    def test_list_modules(self):
        response = self.client.get(self.list_create_url)
        modules = Module.objects.all()
        serializer = ModuleSerializer(modules, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response'], serializer.data)
    
    def test_create_module(self):
        data = {
            'course': self.course.pk,
            'name': 'Module 3',
            'description': 'Description for Module 3',
            'created_by': 'Admin'
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['response']['name'], 'Module 3')
    
    def test_retrieve_module(self):
        response = self.client.get(self.detail_url(self.module1.pk))
        serializer = ModuleSerializer(self.module1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response'], serializer.data)
    
    def test_update_module(self):
        data = {
            'course': self.course.pk,
            'name': 'Updated Module 1',
            'description': 'Updated description',
            'created_by': 'Admin'
        }
        response = self.client.put(self.detail_url(self.module1.pk), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response']['name'], 'Updated Module 1')
    
    def test_delete_module(self):
        response = self.client.delete(self.detail_url(self.module2.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Module.objects.filter(pk=self.module2.pk).exists())

class ToggleActiveStatusAPITests(APITestCase):
    
    def setUp(self):
        self.program = Program.objects.create(
            name='Program to Toggle',
            short_name='PTT',
            description='Description for Program to Toggle',
            created_by='Admin'
        )
        self.course = Course.objects.create(
            program=self.program,
            name='Course to Toggle',
            description='Description for Course to Toggle',
            created_by='Admin',
            credit_hours=4
        )
        self.module = Module.objects.create(
            course=self.course,
            name='Module to Toggle',
            description='Description for Module to Toggle',
            created_by='Admin'
        )
        self.toggle_url = lambda model_name, pk: reverse('toggle_active_status', args=[model_name, pk])
    
    def test_toggle_program_active_status(self):
        response = self.client.patch(self.toggle_url('program', self.program.pk))
        self.program.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.program.is_active, False)
    
    def test_toggle_course_active_status(self):
        response = self.client.patch(self.toggle_url('course', self.course.pk))
        self.course.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.course.is_active, False)
    
    def test_toggle_module_active_status(self):
        response = self.client.patch(self.toggle_url('module', self.module.pk))
        self.module.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.module.is_active, False)
    
    def test_invalid_model_name(self):
        response = self.client.patch(self.toggle_url('invalid_model', self.program.pk))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Invalid model name')
