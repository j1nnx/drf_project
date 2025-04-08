from rest_framework import viewsets, generics, filters
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import Payments, User
from users.permissions import IsOwner
from users.serializer import PaymentsSerializers, UserSerializer
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
)


class PaymentsViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentsSerializers
    queryset = Payments.objects.all()
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ["paid_course", "separately_paid_lesson", "payment_method"]
    ordering_fields = ["payment_date"]


class UserCreateApiView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class UserRetrieveAPIView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwner]


class UserUpdateAPIView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwner]


class UserDestroyAPIView(DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwner]
