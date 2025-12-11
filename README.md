# Django LMS Project

Проект системы управления обучением (LMS) на Django с DRF.

## Функциональность

- Модель пользователя с авторизацией по email
- Курсы и уроки с CRUD операциями
- REST API для работы с данными
- PostgreSQL база данных
- Конфигурация через переменные окружения

## Требования

- Python 3.8+
- PostgreSQL 12+
- Redis (опционально)

## Установка

1. Клонируйте репозиторий:
```bash
git clone <url-репозитория>
cd django-lms-project
```
## Новые API Endpoints

### Пользователи
- `GET /api/users/` - список пользователей
- `POST /api/users/` - создание пользователя
- `GET /api/users/{id}/` - получение пользователя
- `PUT /api/users/{id}/` - обновление пользователя
- `DELETE /api/users/{id}/` - удаление пользователя

### Платежи
- `GET /api/payments/` - список платежей с фильтрацией
- `POST /api/payments/` - создание платежа
- `GET /api/payments/{id}/` - получение платежа

#### Фильтрация платежей:
- `?ordering=payment_date` - сортировка по дате
- `?ordering=-payment_date` - сортировка по дате (убывание)
- `?course=1` - фильтр по курсу
- `?lesson=1` - фильтр по уроку
- `?payment_method=cash` - фильтр по наличным
- `?payment_method=transfer` - фильтр по переводу
- `?payment_date_after=2024-01-01` - платежи после даты
- `?payment_date_before=2024-12-31` - платежи до даты


## Аутентификация и авторизация

### Регистрация
POST /api/register/
Body: {
"email": "user@example.com",
"password": "password",
"password2": "password",
"first_name": "John",
"last_name": "Doe"
}

### Получение JWT токена
POST /api/token/
Body: {
"email": "user@example.com",
"password": "password"
}

### Обновление токена
POST /api/token/refresh/
Body: {
"refresh": "ваш_refresh_токен"
}


## Права доступа

### Модераторы
- Могут просматривать и редактировать все курсы и уроки
- Не могут создавать и удалять курсы/уроки

### Обычные пользователи
- Могут создавать курсы и уроки
- Могут просматривать и редактировать только свои курсы и уроки
- Могут удалять только свои курсы и уроки

## Документация API

Доступна по адресам:
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`
- JSON Schema: `/swagger.json`

## Интеграция с Stripe

### Настройка Stripe

1. Зарегистрируйтесь на [Stripe](https://stripe.com)
2. Получите тестовые ключи из панели управления Stripe
3. Добавьте ключи в `.env` файл:
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

text

### Тестирование оплаты

Используйте тестовые карты Stripe:
- Успешная оплата: `4242 4242 4242 4242`
- Неудачная оплата: `4000 0000 0000 0002`

### Эндпоинты для оплаты

- `POST /api/payments/create-stripe-payment/` - создание платежа через Stripe
- `GET /api/payments/success/` - обработка успешной оплаты
- `GET /api/payments/cancel/` - обработка отмены оплаты
- `GET /api/payments/{id}/status/` - проверка статуса платежа

## Celery и Фоновые Задачи

### Настройка

1. Убедитесь, что Redis запущен:
```bash
redis-server
```

2. Запустите Celery worker:

```bash
celery -A config worker --loglevel=info --pool=solo
Запустите Celery beat (для периодических задач):
```

```bash
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## Запуск с Docker Compose

1. Убедитесь, что у вас установлены Docker и Docker Compose
2. Создайте файл `.env` (опционально, можно указать переменные прямо в docker-compose.yaml)
3. Запустите:
```bash
   docker-compose up -d
```

cat > /home/django/django-lms-project/README.md << 'EOF'
# Django LMS Project

Система управления обучением (Learning Management System), построенная на Django REST Framework.

## 🚀 Продакшен сервер
- **URL**: http://87.228.114.135/
- **API**: http://87.228.114.135/api/courses/
- **Статус**: ✅ Полностью рабочий

## 📋 Настройка проекта

### Требования
- Python 3.11+
- PostgreSQL 14+
- Git
- Ubuntu/Debian сервер

### Локальная разработка
```bash
# Клонировать репозиторий
git clone https://github.com/vladreson/django-lms-project
cd django-lms-project

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
cp .env.template .env
# Отредактировать .env со своими настройками

# Выполнить миграции базы данных
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Запустить сервер разработки
python manage.py runserver
```

🌐 Настройка продакшен сервера
Шаг 1: Подготовка сервера
```bash
# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить необходимые пакеты
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib git -y

# Создать системного пользователя
sudo useradd -m -s /bin/bash django
sudo passwd django  # Установить пароль
```
Шаг 2: Настройка PostgreSQL
```bash
# Войти как postgres
sudo -u postgres psql

# Создать базу данных и пользователя
CREATE DATABASE lms_db;
CREATE USER django WITH PASSWORD 'django';
ALTER USER django CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE lms_db TO django;
\q
```
Шаг 3: Развертывание приложения
```bash
# Войти как пользователь django
sudo su - django

# Клонировать репозиторий
git clone https://github.com/vladreson/django-lms-project
cd django-lms-project

# Настроить виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Настроить переменные окружения
cp .env.template .env
nano .env  # Настроить со своими параметрами

# Собрать статические файлы
python manage.py collectstatic --noinput

# Выполнить миграции
python manage.py migrate
```
Шаг 4: Настройка Gunicorn
```bash
# Создать systemd сервис
sudo nano /etc/systemd/system/gunicorn.service
Добавить:

ini
[Unit]
Description=gunicorn daemon for Django
After=network.target

[Service]
User=django
Group=www-data
WorkingDirectory=/home/django/django-lms-project
ExecStart=/home/django/django-lms-project/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/home/django/django-lms-project/gunicorn.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
bash
# Запустить и включить Gunicorn
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
Шаг 5: Настройка Nginx
bash
sudo nano /etc/nginx/sites-available/django-lms
Добавить:

nginx
server {
    listen 80;
    server_name 87.228.114.135;

    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }

    location /static/ {
        alias /home/django/django-lms-project/static/;
    }

    location /media/ {
        alias /home/django/django-lms-project/media/;
    }

    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://unix:/home/django/django-lms-project/gunicorn.sock;
    }
}
bash
# Включить сайт и перезапустить Nginx
sudo ln -s /etc/nginx/sites-available/django-lms /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
🔄 CI/CD Паipeline
GitHub Actions Workflow
Файл: .github/workflows/deploy.yml

Автоматически запускается при каждом push

Выполняет тесты Django

Деплоит на продакшен при пуше в main ветку

Шаги workflow
Test Job: Запускается на Ubuntu, устанавливает зависимости, выполняет тесты

Deploy Job: Подключается к серверу через SSH, обновляет код, перезапускает сервисы

Необходимые GitHub Secrets
Настроить в Settings → Secrets репозитория:

SERVER_HOST: 87.228.114.135

SERVER_USER: django

SSH_PRIVATE_KEY: Приватный SSH ключ для доступа к серверу

SECRET_KEY: Секретный ключ Django
```
Ручной деплой
```bash
# Подключиться к серверу
ssh django@87.228.114.135

# Обновить код
cd /home/django/django-lms-project
git pull origin main

# Обновить зависимости
source venv/bin/activate
pip install -r requirements.txt

# Применить изменения базы данных
python manage.py migrate

# Собрать статические файлы
python manage.py collectstatic --noinput

# Перезапустить сервисы
sudo systemctl restart gunicorn
sudo systemctl reload nginx
```
🩺 Проверка работоспособности
Статус сервисов
```bash
# Проверить все сервисы
sudo systemctl status nginx      # → active (running)
sudo systemctl status gunicorn   # → active (running)
sudo pg_lsclusters              # → 16 main 5432 online
```
Проверка приложения
```bash
# API endpoint
curl -I http://87.228.114.135/api/courses/
# Ожидаемый результат: HTTP/1.1 200 OK

# Статические файлы
curl -I http://87.228.114.135/static/rest_framework/css/bootstrap.min.css
# Ожидаемый результат: HTTP/1.1 200 OK

# Главная страница
curl -I http://87.228.114.135/
Проверка базы данных
bash
sudo -u postgres psql -d lms_db -c "\dt"
```
🐛 Решение проблем
Частые проблемы
400 Bad Request: Проверить ALLOWED_HOSTS в .env

502 Bad Gateway: Проверить статус Gunicorn

Статические файлы 404: Проверить настройки пути статики в Nginx

Логи
```bash
# Логи Gunicorn
sudo journalctl -u gunicorn -n 50 --no-pager

# Логи доступа Nginx
sudo tail -f /var/log/nginx/access.log

# Логи ошибок Nginx
sudo tail -f /var/log/nginx/error.log

# Логи приложения
cd /home/django/django-lms-project
tail -f debug.log
```
Проблемы с базой данных
```bash
# Проверить PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -c "\l"

# Сбросить базу данных (если нужно)
sudo -u postgres psql -c "DROP DATABASE lms_db;"
sudo -u postgres psql -c "CREATE DATABASE lms_db;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE lms_db TO django;"
cd /home/django/django-lms-project && python manage.py migrate
```
📁 Структура проекта
```text
django-lms-project/
├── .github/workflows/
│   └── deploy.yml          # CI/CD пайплайн
├── config/                 # Настройки Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── materials/              # Приложение курсов
│   ├── models.py
│   ├── views.py
│   └── serializers.py
├── users/                  # Приложение пользователей
├── static/                 # Статические файлы
├── media/                  # Загруженные файлы
├── .env.template           # Шаблон переменных окружения
├── requirements.txt        # Python зависимости
├── manage.py
└── README.md
```
🔧 Переменные окружения
Скопировать .env.template в .env:

```bash
DEBUG=False
SECRET_KEY=ваш-секретный-ключ-здесь
ALLOWED_HOSTS=87.228.114.135,localhost,127.0.0.1
DATABASE_URL=postgres://django:django@localhost:5432/lms_db
```
📞 Поддержка
При возникновении проблем:

Просмотреть логи сервера

Убедиться что все сервисы запущены