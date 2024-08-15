from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from course.models.models import *
from course.serializers import *
from accounts.models.user_models import *
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
import io
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

User = get_user_model()


class ProgramAPITests(APITestCase):
    def setUp(self):
        group_names = ['admin', 'HOD', 'instructor', 'student']
        for name in group_names:
            Group.objects.get_or_create(name=name)

        # Create necessary application entries
        self.application = Applications.objects.create(
            email="admin@example.com",
            first_name="Maaz",
            last_name="Javaid",
            contact="1234567890",
            city="Karachi",
            group_name='student'
        )

        # Create user
        self.user = User.objects.create_user(
            email="admin@example.com", password="password"
        )

        # Create StudentInstructor entry
        # Assume 'session' and 'batch' are available in your test environment or create mock instances
        self.session = Sessions.objects.create(name='Test Session')
        self.batch = Batch.objects.create(batch='Test Batch')
        StudentInstructor.objects.create(
            user=self.user,
            session=self.session,
            batch=self.batch
        )


        # Obtain JWT tokens
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Set JWT token in client
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

        self.program1 = Program.objects.create(
            name="Program 1",
            short_description="P1",
            about="Description for Program 1",
            created_by=self.user,
        )
        self.program2 = Program.objects.create(
            name="Program 2",
            short_description="P2",
            about="Description for Program 2",
            created_by=self.user,
        )
        self.list_create_url = reverse("program-list-create")
        self.detail_url = lambda pk: reverse("program-detail", args=[pk])

    def test_list_programs(self):
        response = self.client.get(self.list_create_url)
        programs = Program.objects.all()
        serializer = ProgramSerializer(programs, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status_code"], status.HTTP_200_OK)
        self.assertEqual(response.data["response"], serializer.data)

    def test_create_program(self):
        data = {
            "name": "Program 3",
            "short_description": "P3",
            "about": "Description for Program 3",
            "status": 0,
        }
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["response"]["name"], "Program 3")

    def test_retrieve_program(self):
        response = self.client.get(self.detail_url(self.program1.pk))
        serializer = ProgramSerializer(self.program1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["response"], serializer.data)

    def test_update_program(self):
        data = {
            "name": "Updated Program 1",
            "short_description": "UP1",
            "about": "Updated description",
        }
        response = self.client.put(
            self.detail_url(self.program1.pk), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["response"]["name"], "Updated Program 1")

    def test_delete_program(self):
        response = self.client.delete(self.detail_url(self.program2.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Program.objects.filter(pk=self.program2.pk).exists())


# class CourseAPITests(APITestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(email='admin@example.com', password='password')

#         # Obtain JWT tokens
#         refresh = RefreshToken.for_user(self.user)
#         self.access_token = str(refresh.access_token)

#         # Set JWT token in client
#         self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

#         self.program = Program.objects.create(
#             name='Program for Courses',
#             short_name='PFC',
#             description='Description for Program for Courses',
#             created_by=self.user
#         )
#         self.course1 = Course.objects.create(
#             program=self.program,
#             name='Course 1',
#             description='Description for Course 1',
#             created_by=self.user,
#             credit_hours=4
#         )
#         self.course2 = Course.objects.create(
#             program=self.program,
#             name='Course 2',
#             description='Description for Course 2',
#             created_by=self.user,
#             credit_hours=3
#         )
#         self.list_create_url = reverse('course-list-create')
#         self.detail_url = lambda pk: reverse('course-detail', args=[pk])

#     def test_list_courses(self):
#         response = self.client.get(self.list_create_url)
#         courses = Course.objects.all()
#         serializer = CourseSerializer(courses, many=True)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['response'], serializer.data)

#     def test_create_course(self):
#         data = {
#             'program': self.program.pk,
#             'name': 'Course 3',
#             'description': 'Description for Course 3',
#             'created_by': self.user.id,  # Pass user ID instead of user object
#             'credit_hours': 5
#         }
#         response = self.client.post(self.list_create_url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data['response']['name'], 'Course 3')

#     def test_retrieve_course(self):
#         response = self.client.get(self.detail_url(self.course1.pk))
#         serializer = CourseSerializer(self.course1)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['response'], serializer.data)

#     def test_update_course(self):
#         data = {
#             'program': self.program.pk,
#             'name': 'Updated Course 1',
#             'description': 'Updated description',
#             'created_by': self.user.id,  # Pass user ID instead of user object
#             'credit_hours': 6
#         }
#         response = self.client.put(self.detail_url(self.course1.pk), data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['response']['name'], 'Updated Course 1')

#     def test_delete_course(self):
#         response = self.client.delete(self.detail_url(self.course2.pk))
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertFalse(Course.objects.filter(pk=self.course2.pk).exists())

# class ModuleAPITests(APITestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(email='admin@example.com', password='password')

#         # Obtain JWT tokens
#         refresh = RefreshToken.for_user(self.user)
#         self.access_token = str(refresh.access_token)

#         # Set JWT token in client
#         self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

#         self.program = Program.objects.create(
#             name='Program for Modules',
#             short_name='PFM',
#             description='Description for Program for Modules',
#             created_by=self.user  # Use user object
#         )
#         self.course = Course.objects.create(
#             program=self.program,
#             name='Course for Modules',
#             description='Description for Course for Modules',
#             created_by=self.user,  # Use user object
#             credit_hours=4
#         )
#         self.module1 = Module.objects.create(
#             course=self.course,
#             name='Module 1',
#             description='Description for Module 1',
#             created_by=self.user  # Use user object
#         )
#         self.module2 = Module.objects.create(
#             course=self.course,
#             name='Module 2',
#             description='Description for Module 2',
#             created_by=self.user  # Use user object
#         )
#         self.list_create_url = reverse('module-list-create')
#         self.detail_url = lambda pk: reverse('module-detail', args=[pk])

#     def test_list_modules(self):
#         response = self.client.get(self.list_create_url)
#         modules = Module.objects.all()
#         serializer = ModuleSerializer(modules, many=True)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['response'], serializer.data)

#     def test_create_module(self):
#         data = {
#             'course': self.course.pk,
#             'name': 'Module 3',
#             'description': 'Description for Module 3',
#             'created_by': self.user.id  # Use user ID instead of user object
#         }
#         response = self.client.post(self.list_create_url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data['response']['name'], 'Module 3')

#     def test_retrieve_module(self):
#         response = self.client.get(self.detail_url(self.module1.pk))
#         serializer = ModuleSerializer(self.module1)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['response'], serializer.data)

#     def test_update_module(self):
#         data = {
#             'course': self.course.pk,
#             'name': 'Updated Module 1',
#             'description': 'Updated description',
#             'created_by': self.user.id  # Use user ID instead of user object
#         }
#         response = self.client.put(self.detail_url(self.module1.pk), data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['response']['name'], 'Updated Module 1')

#     def test_delete_module(self):
#         response = self.client.delete(self.detail_url(self.module2.pk))
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertFalse(Module.objects.filter(pk=self.module2.pk).exists())


# class ToggleActiveStatusAPITests(APITestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(email='admin@example.com', password='password')
#         refresh = RefreshToken.for_user(self.user)
#         self.access_token = str(refresh.access_token)
#         self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

#         self.program = Program.objects.create(
#             name='Program to Toggle',
#             short_name='PTT',
#             description='Description for Program to Toggle',
#             created_by=self.user
#         )
#         self.course = Course.objects.create(
#             program=self.program,
#             name='Course to Toggle',
#             description='Description for Course to Toggle',
#             created_by=self.user,
#             credit_hours=4
#         )
#         self.module = Module.objects.create(
#             course=self.course,
#             name='Module to Toggle',
#             description='Description for Module to Toggle',
#             created_by=self.user
#         )
#         self.toggle_url = lambda model_name, pk: reverse('toggle_active_status', args=[model_name, pk])

#     def test_toggle_program_active_status(self):
#         response = self.client.patch(self.toggle_url('programs', self.program.pk))
#         self.program.refresh_from_db()
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertNotEqual(self.program.is_active, True)

#     def test_toggle_course_active_status(self):
#         response = self.client.patch(self.toggle_url('courses', self.course.pk))
#         self.course.refresh_from_db()
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertNotEqual(self.course.is_active, True)

#     def test_toggle_module_active_status(self):
#         response = self.client.patch(self.toggle_url('modules', self.module.pk))
#         self.module.refresh_from_db()
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertNotEqual(self.module.is_active, True)

#     def test_invalid_model_name(self):
#         response = self.client.patch(self.toggle_url('invalid_model', self.program.pk))
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['message'], 'Invalid model name')


# class ContentAPITestCase(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(email='admin@example.com', password='password')

#         # Obtain JWT tokens
#         refresh = RefreshToken.for_user(self.user)
#         self.access_token = str(refresh.access_token)

#         # Set JWT token in client
#         self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)


#         # Create a Course instance
#         self.course = Course.objects.create(name='Test Course', description='Test Course Description',
#             credit_hours=3,created_by=self.user )

#         # Create a Module instance associated with the Course
#         self.module = Module.objects.create(name='Test Module', course=self.course,created_by=self.user)

#         self.content_url = reverse('content-list-create')
#         self.content_data = {
#             'module': self.module.id,
#             'name': 'Test Content'
#         }

#     def test_create_content(self):
#         response = self.client.post(self.content_url, self.content_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Content.objects.count(), 1)
#         self.assertEqual(Content.objects.get().name, 'Test Content')

#     def test_get_contents(self):
#         Content.objects.create(module=self.module, name='Test Content')
#         response = self.client.get(self.content_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['response']), 1)


#     def test_update_content(self):
#         content = Content.objects.create(module=self.module, name='Test Content')
#         url = reverse('content-detail', args=[content.id])
#         updated_data = {'module': self.module.id, 'name': 'Updated Content'}
#         response = self.client.put(url, updated_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         content.refresh_from_db()
#         self.assertEqual(content.name, 'Updated Content')

#     def test_delete_content(self):
#         content = Content.objects.create(module=self.module, name='Test Content')
#         url = reverse('content-detail', args=[content.id])
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertEqual(Content.objects.count(), 0)


# class ContentFileAPITestCase(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(email='admin@example.com', password='password')

#         # Obtain JWT tokens
#         refresh = RefreshToken.for_user(self.user)
#         self.access_token = str(refresh.access_token)

#         # Set JWT token in client
#         self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

#         self.course = Course.objects.create(name='Test Course', description='Test Course Description',
#                                             credit_hours=3, created_by=self.user)
#         self.module = Module.objects.create(name='Test Module', created_by=self.user, course=self.course)
#         self.content = Content.objects.create(module=self.module, name='Test Content')

#         self.content_file_url = reverse('content-file-list-create')
#         self.file = SimpleUploadedFile("file.pdf", b"file_content", content_type="application/pdf")
#         self.content_file_data = {
#             'content': self.content.id,
#             'file': self.file,
#         }

#     # def test_create_content_file(self):
#     #     response = self.client.post(self.content_file_url, self.content_file_data, format='multipart')
#     #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#     #     self.assertEqual(ContentFile.objects.count(), 1)
#     #     content_file = ContentFile.objects.first()
#     #     self.assertEqual(content_file.content.id, self.content.id)
#     #     self.assertEqual(content_file.file.name, 'content/file.pdf')


#     def test_get_content_files(self):
#         ContentFile.objects.create(content=self.content, file=self.file)
#         response = self.client.get(self.content_file_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['response']), 1)

#     def test_update_content_file(self):
#         content_file = ContentFile.objects.create(content=self.content, file=self.file)
#         url = reverse('content-file-detail', args=[content_file.id])
#         new_file = SimpleUploadedFile("new_file.pdf", b"new_file_content", content_type="application/pdf")
#         updated_data = {'content': self.content.id, 'file': new_file}
#         response = self.client.put(url, updated_data, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         content_file.refresh_from_db()

#         # Check that the new file is indeed present
#         self.assertTrue(content_file.file.name.startswith('content/new_file'))
#         self.assertTrue(content_file.file.name.endswith('.pdf'))

#     def test_delete_content_file(self):
#         content_file = ContentFile.objects.create(content=self.content, file=self.file)
#         url = reverse('content-file-detail', args=[content_file.id])
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertEqual(ContentFile.objects.count(), 0)


# class AssignmentAPITests(APITestCase):


#     def setUp(self):
#         self.user = User.objects.create_user(email='admin@example.com', password='password')
#         refresh = RefreshToken.for_user(self.user)
#         self.access_token = str(refresh.access_token)
#         self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
#         self.course = Course.objects.create(name='Test Course', description='Test Course Description',
#                                             credit_hours=3, created_by=self.user)
#         # self.module = Module.objects.create(name='Test Module', created_by=self.user, course=self.course)
#         self.now = timezone.now()
#         self.assignment1 = Assignment.objects.create(
#             course=self.course,
#             created_at=self.now,
#             question='What is the assignment?',
#             description='Description for assignment 1',
#             content='Content for assignment 1',
#             total_marks=100,
#             due_date=self.now + timezone.timedelta(days=15),
#             is_active=True
#         )
#         self.assignment2 = Assignment.objects.create(
#             course=self.course,
#             created_at=self.now,
#             question='Another assignment?',
#             description='Description for assignment 2',
#             content='Content for assignment 2',
#             total_marks=50,
#             due_date=self.now + timezone.timedelta(days=20),
#             is_active=True
#         )
#         self.list_create_url = reverse('assignment-list-create')
#         self.detail_url = lambda pk: reverse('assignment-detail', args=[pk])

#     def test_list_assignments(self):
#         response = self.client.get(self.list_create_url)
#         assignments = Assignment.objects.all()
#         serializer = AssignmentSerializer(assignments, many=True)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['status_code'], status.HTTP_200_OK)
#         self.assertEqual(response.data['response'], serializer.data)

#     def test_create_assignment(self):
#         file = SimpleUploadedFile("content.txt", b"file content", content_type="text/plain")
#         data = {
#             'course': self.course.pk,
#             'created_at': '2024-07-31T00:00:00Z',
#             'question': 'New assignment?',
#             'description': 'Description for assignment 3',
#             'content': file,  # Provide a file object here
#             'total_marks': 75,
#             'due_date': '2024-08-25T00:00:00Z',
#             'is_active': True
#         }
#         response = self.client.post(self.list_create_url, data, format='multipart')  # Use multipart format for file uploads
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data['response']['question'], 'New assignment?')

#     def test_retrieve_assignment(self):
#         response = self.client.get(self.detail_url(self.assignment1.pk))
#         serializer = AssignmentSerializer(self.assignment1)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['response'], serializer.data)

#     def test_update_assignment(self):
#         data = {
#             'question': 'Updated question?',
#             'description': 'Updated description',
#         }
#         response = self.client.put(self.detail_url(self.assignment1.pk), data, format='json')
#         print(response)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['response']['question'], 'Updated question?')

#     def test_delete_assignment(self):
#         response = self.client.delete(self.detail_url(self.assignment2.pk))
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertFalse(Assignment.objects.filter(pk=self.assignment2.pk).exists())


# class AssignmentSubmissionAPITests(APITestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(email='admin@example.com', password='password')
#         refresh = RefreshToken.for_user(self.user)
#         self.access_token = str(refresh.access_token)
#         self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

#         self.course = Course.objects.create(name='Test Course', description='Test Course Description',
#                                             credit_hours=3, created_by=self.user)
#         self.assignment = Assignment.objects.create(
#             course=self.course,
#             created_at=timezone.now(),
#             question='What is the assignment?',
#             description='Description for assignment 1',
#             content='Content for assignment 1',
#             total_marks=100,
#             due_date=timezone.now() + timezone.timedelta(days=15),
#             is_active=True
#         )
#         self.assignment_submission1 = AssignmentSubmission.objects.create(
#             assignment=self.assignment,
#             user=self.user,
#             submitted_file=SimpleUploadedFile("file1.pdf", b"file content", content_type="application/pdf")
#         )
#         self.assignment_submission2 = AssignmentSubmission.objects.create(
#             assignment=self.assignment,
#             user=self.user,
#             submitted_file=SimpleUploadedFile("file2.pdf", b"file content", content_type="application/pdf")
#         )
#         self.list_create_url = reverse('submission-create')
#         self.detail_url = lambda pk: reverse('submission-detail', args=[pk])

#     # def test_list_assignment_submissions(self):
#     #     response = self.client.get(self.list_create_url)
#     #     print(response)
#     #     submissions = AssignmentSubmission.objects.all()

#     #     serializer = AssignmentSubmissionSerializer(submissions, many=True)
#     #     print(serializer.data)
#     #     self.assertEqual(response.status_code, status.HTTP_200_OK)
#     #     self.assertEqual(response.data['status_code'], status.HTTP_200_OK)
#     #     self.assertEqual(response.data['response'], serializer.data)

#     def test_create_assignment_submission(self):
#         file = SimpleUploadedFile("new_file.pdf", b"new file content", content_type="application/pdf")
#         data = {
#             'assignment': self.assignment.pk,
#             'user': self.user.pk,
#             'submitted_file': file,
#         }
#         response = self.client.post(self.list_create_url, data, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data['response']['submitted_file'], 'new_file.pdf')
