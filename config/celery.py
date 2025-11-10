import os
from celery import Celery
from celery.schedules import crontab

# Установка переменной окружения для настроек проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Использование строки настроек из настроек проекта
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач из всех зарегистрированных приложений Django
app.autodiscover_tasks()

# Расписание периодических задач
app.conf.beat_schedule = {
    'block-inactive-users-monthly': {
        'task': 'users.tasks.block_inactive_users',
        'schedule': crontab(day_of_month='1', hour=0, minute=0),  # Первое число каждого месяца в 00:00
    },
    'check-course-updates-hourly': {
        'task': 'materials.tasks.check_course_updates',
        'schedule': crontab(minute=0, hour='*/1'),  # Каждый час
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')