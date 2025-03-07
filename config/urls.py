from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("course.urls", namespace="course")),
    path("users/", include("users.urls", namespace="users")),
]
