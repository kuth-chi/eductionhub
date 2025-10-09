"""
Tests for Resume/CV API endpoints
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from organization.models.base import Organization
from schools.models.online_profile import Platform
from schools.models.school import School
from user.models.base import (Education, Experience, Hobby, Language, Letter,
                              ProfileContact, Reference, Skill)
from user.models.profile import Profile

User = get_user_model()


class ResumeAPITestCase(TestCase):
    """Test suite for resume/CV API endpoints"""

    def setUp(self):
        """Set up test data"""
        # Create test user and profile
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.profile = Profile.objects.create(user=self.user)

        # Create another user for permission testing
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        self.other_profile = Profile.objects.create(user=self.other_user)

        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_experience(self):
        """Test creating a work experience entry"""
        data = {
            "title": "Software Engineer",
            "start_date": "2020-01-01",
            "end_date": "2022-12-31",
            "responsibilities": "Developed web applications",
        }
        response = self.client.post(
            "/api/v1/user-experiences/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Experience.objects.count(), 1)
        self.assertEqual(Experience.objects.first().user, self.profile)

    def test_list_user_experiences(self):
        """Test listing only the current user's experiences"""
        # Create experience for test user
        Experience.objects.create(
            user=self.profile,
            title="Software Engineer",
            start_date="2020-01-01",
            end_date="2022-12-31",
            responsibilities="Developed web applications",
        )
        # Create experience for other user
        Experience.objects.create(
            user=self.other_profile,
            title="Data Scientist",
            start_date="2019-01-01",
            end_date="2021-12-31",
            responsibilities="Analyzed data",
        )

        response = self.client.get("/api/v1/user-experiences/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return current user's experience
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Software Engineer")

    def test_update_experience(self):
        """Test updating an experience entry"""
        experience = Experience.objects.create(
            user=self.profile,
            title="Software Engineer",
            start_date="2020-01-01",
            end_date="2022-12-31",
            responsibilities="Developed web applications",
        )

        data = {"title": "Senior Software Engineer"}
        response = self.client.patch(
            f"/api/v1/user-experiences/{experience.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        experience.refresh_from_db()
        self.assertEqual(experience.title, "Senior Software Engineer")

    def test_delete_experience(self):
        """Test deleting an experience entry"""
        experience = Experience.objects.create(
            user=self.profile,
            title="Software Engineer",
            start_date="2020-01-01",
            end_date="2022-12-31",
            responsibilities="Developed web applications",
        )

        response = self.client.delete(
            f"/api/v1/user-experiences/{experience.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Experience.objects.count(), 0)

    def test_create_education(self):
        """Test creating an education entry"""
        data = {
            "degree": "Bachelor of Science in Computer Science",
            "start_date": "2015-09-01",
            "end_date": "2019-06-30",
            "description": "Focused on software engineering",
        }
        response = self.client.post(
            "/api/v1/user-education/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Education.objects.count(), 1)

    def test_create_skill(self):
        """Test creating a skill entry"""
        data = {"name": "Python", "level": "Expert"}
        response = self.client.post(
            "/api/v1/user-skills/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Skill.objects.count(), 1)

    def test_create_language(self):
        """Test creating a language entry"""
        data = {"name": "English", "level": "Native", "is_native": True}
        response = self.client.post(
            "/api/v1/user-languages/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Language.objects.count(), 1)

    def test_create_hobby(self):
        """Test creating a hobby entry"""
        data = {"name": "Photography"}
        response = self.client.post(
            "/api/v1/user-hobbies/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Hobby.objects.count(), 1)

    def test_create_reference(self):
        """Test creating a reference entry"""
        data = {
            "name": "John Doe",
            "position": "Senior Manager",
            "relationship": "Former supervisor",
            "phone": "+1234567890",
            "email": "john.doe@example.com",
        }
        response = self.client.post(
            "/api/v1/user-references/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reference.objects.count(), 1)

    def test_create_letter(self):
        """Test creating a letter/cover letter"""
        data = {
            "title": "Software Engineer Application",
            "content": "Dear Hiring Manager, I am writing to apply...",
        }
        response = self.client.post(
            "/api/v1/user-letters/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Letter.objects.count(), 1)
        self.assertEqual(Letter.objects.first().user, self.user)

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access the API"""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/user-experiences/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_access_other_user_data(self):
        """Test that users cannot see other users' data"""
        # Create experience for other user
        other_experience = Experience.objects.create(
            user=self.other_profile,
            title="Data Scientist",
            start_date="2019-01-01",
            end_date="2021-12-31",
            responsibilities="Analyzed data",
        )

        # Try to access other user's experience
        response = self.client.get(
            f"/api/v1/user-experiences/{other_experience.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def tearDown(self):
        """Clean up test data"""
        User.objects.all().delete()
        Profile.objects.all().delete()
        Experience.objects.all().delete()
        Education.objects.all().delete()
        Skill.objects.all().delete()
        Language.objects.all().delete()
        Hobby.objects.all().delete()
        Reference.objects.all().delete()
        Letter.objects.all().delete()
