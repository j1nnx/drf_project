from datetime import timezone
import stripe
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from course.models import Course, Lessons, Subscription
from course.paginations import CustomPagination
from course.serializers import CourseSerializer, LessonsSerializer
from users.models import Payments
from users.permissions import IsModer, IsOwner
from users.services import create_stripe_product, create_stripe_price, create_stripe_session
from .tasks import send_course_update_notifications


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="description from swagger_auto_schema via method_decorator"))
class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ["create"]:
            self.permission_classes = (~IsModer,)
        elif self.action in ["update", "retrieve"]:
            self.permission_classes = (IsModer | IsOwner,)
        elif self.action == "destroy":
            self.permission_classes = (IsOwner | ~IsModer,)
        return super().get_permissions()

    pagination_class = CustomPagination

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        send_course_update_notifications.delay(instance.id)

        return Response(serializer.data, status=status.HTTP_200_OK)


class LessonsViewSet(ModelViewSet):
    queryset = Lessons.objects.all()
    serializer_class = LessonsSerializer
    permission_classes = (~IsModer, IsAuthenticated)


class LessonsCreateApiView(CreateAPIView):
    queryset = Lessons.objects.all()
    serializer_class = LessonsSerializer
    permission_classes = (IsAuthenticated,)


class LessonsListAPIView(ListAPIView):
    queryset = Lessons.objects.all()
    serializer_class = LessonsSerializer
    pagination_class = CustomPagination


class LessonsRetrieveAPIView(RetrieveAPIView):
    queryset = Lessons.objects.all()
    serializer_class = LessonsSerializer
    permission_classes = (IsAuthenticated, IsModer | IsOwner)


class LessonsUpdateAPIView(UpdateAPIView):
    queryset = Lessons.objects.all()
    serializer_class = LessonsSerializer
    permission_classes = (IsAuthenticated, IsModer | IsOwner)


class LessonsDestroyAPIView(DestroyAPIView):
    queryset = Lessons.objects.all()
    serializer_class = LessonsSerializer
    permission_classes = (IsAuthenticated, IsOwner | ~IsModer)


class SubscriptionView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            return Response(
                {"error": "Course ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        course = get_object_or_404(Course, id=course_id)
        subscription, created = Subscription.objects.get_or_create(
            user=user, course=course
        )

        if created:
            message = "Подписка добавлена"
            status_code = status.HTTP_201_CREATED
        else:
            subscription.delete()
            message = "Подписка удалена"
            status_code = status.HTTP_204_NO_CONTENT

        return Response({"message": message}, status=status_code)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_payment(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        user = request.user if request.user.is_authenticated else None
        product = create_stripe_product(course)
        product_id = product.id
        price = create_stripe_price(course.price, product_id)
        price_id = price.id
        payment = Payments.objects.create(
            user=user,
            paid_course=course,
            payment_amount=course.price,
            payment_method="stripe",
            stripe_status="pending",
        )
        success_url = "http://127.0.0.1:8000/success/"
        cancel_url = "http://127.0.0.1:8000/cancel/"
        session_id, session_url = create_stripe_session(price_id, success_url, cancel_url, course_id, user.id)
        payment.stripe_session_id = session_id
        payment.save()

        return Response({"payment_url": session_url})
    except Course.DoesNotExist:
        return Response({"error": "Курс не найден"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
def payment_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return Response({"error": "Session ID не предоставлен"}, status=400)

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            payment = Payments.objects.get(stripe_session_id=session_id)
            payment.stripe_status = "completed"
            payment.payment_date = timezone.now()
            payment.save()
            return Response({"message": "Оплата успешно завершена"})
        else:
            return Response({"error": "Оплата не завершена"}, status=400)
    except Payments.DoesNotExist:
        return Response({"error": "Платеж не найден"}, status=404)
    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
def payment_cancel(request):
    return Response({"message": "Оплата отменена"})



