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