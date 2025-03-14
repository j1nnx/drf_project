from datetime import timezone, timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from course.models import Subscription, Course

User = get_user_model()


@shared_task
def send_course_update_notifications(course_id):
    try:
        course = Course.objects.get(id=course_id)
        subscriptions = Subscription.objects.filter(course=course)
        if not subscriptions.exists():
            print(f"Нет подписчиков на курс {course.name}")
            return

        subject = f"Обновление курса: {course.name}"
        message = (f"Здравствуйте!\n\nКурс '{course.name}' был обновлен."
                   f" Проверьте новые материалы!\n\nС уважением,\nКоманда курса")
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [sub.user.email for sub in subscriptions if sub.user.email]

        if recipient_list:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            print(f"Уведомления отправлены {len(recipient_list)} подписчикам курса {course.name}")
        else:
            print(f"Нет валидных email для курса {course.name}")
    except Exception as e:
        print(f"Ошибка при отправке уведомлений: {str(e)}")


@shared_task
def deactivate_inactive_users():
    threshold_date = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(last_login__lt=threshold_date, is_active=True)

    if not inactive_users.exists():
        print("Нет пользователей для деактивации")
        return

    count = inactive_users.update(is_active=False)
    print(f"Деактивировано {count} пользователей, не заходивших более месяца")