# ERD - Entity Relationship Diagram

## Структура базы данных Football Club

```
┌─────────────────────┐
│      USERS          │
├─────────────────────┤
│ id (PK)             │
│ email               │
│ password            │
│ name                │
│ role                │
│ created_at          │
└─────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────────┐       ┌─────────────────────┐
│     ORDERS          │       │   ORDER_ITEMS       │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │───────│ id (PK)             │
│ user_id (FK)        │  1:N  │ order_id (FK)       │
│ product_id (FK)     │       │ product_id (FK)     │
│ ticket_id (FK)      │       │ quantity            │
│ total_price         │       │ price               │
│ status              │       └─────────────────────┘
│ user_data           │                │
│ created_at          │                │
└─────────────────────┘                │
         │                             │
         │                             │
    ┌────┴────┐                        │
    │         │                        │
    ▼         ▼                        ▼
┌─────────────────────┐       ┌─────────────────────┐
│    PRODUCTS         │       │     TICKETS         │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │       │ id (PK)             │
│ name                │       │ match_id (FK)       │
│ price               │       │ sector              │
│ image               │       │ row                 │
│ size                │       │ seat                │
│ in_stock            │       │ price               │
│ description         │       │ available           │
└─────────────────────┘       └─────────────────────┘
                                       │
                                       │ N:1
                                       ▼
                              ┌─────────────────────┐
                              │     MATCHES         │
                              ├─────────────────────┤
                              │ id (PK)             │
                              │ home_team           │
                              │ away_team           │
                              │ date                │
                              │ time                │
                              │ stadium             │
                              │ score               │
                              │ home_team_logo      │
                              │ away_team_logo      │
                              └─────────────────────┘

┌─────────────────────┐       ┌─────────────────────┐
│    PLAYERS          │       │   TRANSFERS         │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │       │ id (PK)             │
│ name                │       │ player_name         │
│ position            │       │ from_club           │
│ number              │       │ to_club             │
│ age                 │       │ transfer_type       │
│ photo               │       │ date                │
│ bio                 │       │ amount              │
└─────────────────────┘       │ player_photo        │
                              │ from_club_logo      │
                              │ to_club_logo        │
                              └─────────────────────┘

┌─────────────────────┐       ┌─────────────────────┐
│      NEWS           │       │ PAYMENT_METHODS     │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │       │ id (PK)             │
│ title               │       │ user_id (FK)        │
│ content             │       │ card_number         │
│ image               │       │ card_holder         │
│ date                │       │ expiry_date         │
│ category            │       │ is_default          │
└─────────────────────┘       │ created_at          │
                              └─────────────────────┘
                                       │
                                       │ N:1
                                       ▼
                              ┌─────────────────────┐
                              │      USERS          │
                              └─────────────────────┘
```

## Связи между таблицами

### 1:N (One-to-Many)
- **USERS → ORDERS**: Один пользователь может иметь много заказов
- **USERS → PAYMENT_METHODS**: Один пользователь может иметь много способов оплаты
- **ORDERS → ORDER_ITEMS**: Один заказ может содержать много товаров
- **MATCHES → TICKETS**: Один матч может иметь много билетов

### N:1 (Many-to-One)
- **ORDER_ITEMS → PRODUCTS**: Много позиций заказа могут ссылаться на один товар
- **TICKETS → MATCHES**: Много билетов относятся к одному матчу
- **ORDERS → PRODUCTS**: Заказ может содержать товары (через ORDER_ITEMS)
- **ORDERS → TICKETS**: Заказ может содержать билеты

## Ключевые поля

### Primary Keys (PK)
Все таблицы используют `id INTEGER PRIMARY KEY AUTOINCREMENT`

### Foreign Keys (FK)
- `user_id` - связь с таблицей USERS
- `product_id` - связь с таблицей PRODUCTS
- `ticket_id` - связь с таблицей TICKETS
- `match_id` - связь с таблицей MATCHES
- `order_id` - связь с таблицей ORDERS

## Типы данных

- **INTEGER**: id, user_id, product_id, age, number, quantity
- **TEXT**: email, password, name, role, title, content, image
- **REAL**: price, total_price
- **TIMESTAMP**: created_at (DEFAULT CURRENT_TIMESTAMP)
- **BOOLEAN**: in_stock, available, is_default (0 или 1)
