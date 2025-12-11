# API Документация - Football Club Website

## Базовый URL
```
http://localhost:5000/api
```

## Swagger UI
```
http://localhost:5000/swagger/
```

## Аутентификация

### POST /auth/register
Регистрация нового пользователя
```json
{
  "contact": "user@example.com",
  "password": "password123",
  "name": "Иван Иванов"
}
```

### POST /auth/login
Вход в систему
```json
{
  "contact": "admin@anzhi.ru",
  "password": "admin123"
}
```

## Товары (Products)

### GET /products
Получить список всех товаров

### GET /products/{id}
Получить товар по ID

## Билеты (Tickets)

### GET /tickets
Получить список всех билетов

### GET /tickets/{id}
Получить билет по ID

### POST /tickets (Admin)
Создать новый билет

## Матчи (Matches)

### GET /matches
Получить список всех матчей

### GET /matches/{id}
Получить матч по ID

### POST /matches (Admin)
Создать новый матч

## Трансферы (Transfers)

### GET /transfers
Получить список всех трансферов

### POST /transfers (Admin)
Создать новый трансфер

## Игроки (Players)

### GET /players
Получить список всех игроков

### GET /players/{id}
Получить игрока по ID

## Новости (News)

### GET /news
Получить список всех новостей

### POST /news (Admin)
Создать новость

## Заказы (Orders)

### POST /orders
Создать заказ

### GET /profile/orders
Получить историю заказов пользователя (требуется авторизация)

## Профиль (Profile)

### GET /profile
Получить данные профиля (требуется авторизация)

### PUT /profile
Обновить данные профиля (требуется авторизация)

## Авторизация
Для защищённых эндпоинтов необходимо передавать JWT токен в заголовке:
```
Authorization: Bearer <token>
```

## Роли
- **user** - обычный пользователь
- **admin** - администратор (может создавать матчи, трансферы, новости)
