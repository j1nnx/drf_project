from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from course.models import Course, Lessons, Subscription
from users.models import User


class CourseTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="admin@sky.pro")
        self.course = Course.objects.create(title="Уроки Пашки")
        Lessons.objects.all().delete()
        self.lesson = Lessons.objects.create(
            title="Урок по созданию денег",
            course=self.course,
            video_url="https://youtube.com/sample_video",
            owner=self.user,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_lesson(self):
        data = {
            "title": "Новый урок",
            "description": "Описание нового урока",
            "video_url": "https://youtube.com/sample_video_2",
            "course": self.course.id,
        }
        response = self.client.post("/lessons/create/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lessons.objects.count(), 2)

    def test_get_lessons(self):
        response = self.client.get("/lessons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_update_lesson(self):
        data = {
            "title": "Мишин урок",
            "description": "Описание Мишиного урока",
            "video_url": "https://youtube.com/updated_video",
            "course": self.course.id,
        }
        response = self.client.put(
            f"/lessons/{self.lesson.id}/update/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Мишин урок")

    def test_delete_lesson(self):
        response = self.client.delete(f"/lessons/{self.lesson.id}/delete/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lessons.objects.count(), 0)


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@example.com")
        self.course = Course.objects.create(title="Курс по Python")
        self.client.force_authenticate(user=self.user)

    def test_subscribe_to_course(self):
        data = {"course_id": self.course.id}
        response = self.client.post("/subscribe/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscription.objects.count(), 1)
        subscription = Subscription.objects.first()
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.course, self.course)

    def test_unsubscribe_from_course(self):
        Subscription.objects.create(user=self.user, course=self.course)
        data = {"course_id": self.course.id}
        response = self.client.post("/subscribe/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Subscription.objects.count(), 0)
