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