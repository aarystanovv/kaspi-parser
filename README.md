# Парсер Kaspi магазина

## 📌 Описание проекта
Сервис на FastAPI парсит карточку товара Kaspi и сохраняет данные:
- что парсит: название, категория, мин/макс цена, рейтинг, отзывы, (опц.) характеристики, изображения, количество продавцов, офферы
- куда сохраняет: PostgreSQL (таблицы `products`, `offers`), JSON (`export/product.json`, `export/offers.jsonl`)
- дополнительно: автообновление (15 минут), JSON-логирование, Docker, Alembic миграции

## 🛠️ Стек технологий
- **Python 3.11+**
- **FastAPI** — асинхронный REST API
- **SQLAlchemy 2.0** — ORM (используется `AsyncSession` + `asyncpg` для полностью асинхронной работы с БД)
- **asyncpg** — асинхронный PostgreSQL-драйвер
- **httpx** — асинхронный HTTP-клиент для парсинга
- **BeautifulSoup4 + lxml** — парсинг HTML
- **Alembic** — миграции БД
- **APScheduler** — фоновое обновление данных
- **structlog** — структурированное JSON-логирование
- **Docker + Docker Compose**

## 🚀 Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/<username>/<repo>.git
cd <repo>
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Настройка окружения
Создайте `.env` по примеру:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=kaspi
DB_USER=postgres
DB_PASSWORD=postgres
APP_ENV=development
LOG_LEVEL=info
SCHEDULER_ENABLED=false
EXPORT_DIR=export
LOG_DIR=logs
```

### 4. Инициализация БД
- Запустите PostgreSQL и создайте БД `kaspi`.
- Примените миграции Alembic:
```bash
alembic upgrade head
```

### 5. Запуск парсера (один запуск)
```bash
python main.py
```

### 6. Запуск API
```bash
uvicorn app.main:app --reload
```

## ▶️ Docker
Запуск всего стека:
```bash
docker compose up --build
```
Миграции внутри контейнера (если нужно):
```bash
docker compose exec app alembic upgrade head
```

## 📂 Структура проекта
```
/project
│── main.py
│── seed.json
│── export/
│    ├── product.json
│    ├── offers.jsonl
│── app/
│    ├── main.py
│    ├── api/
│    │   └── routes.py
│    ├── core/
│    │   └── config.py
│    ├── db/
│    │   ├── base.py
│    │   ├── models.py
│    │   └── session.py
│    ├── schemas/
│    │   └── product.py
│    ├── services/
│    │   └── parser.py
│    ├── repositories/
│    │   └── product_repository.py
│    ├── logging_config.py
│    ├── exporter.py
│    └── scheduler.py
│── alembic/
│    ├── env.py
│    ├── README
│    ├── script.py.mako
│    └── versions/
│         └── 0001_init.py
│── logs/
│    └── log.json
│── Dockerfile
│── docker-compose.yml
│── README.md
```

## 🗄️ PostgreSQL
Таблицы:

**products**
| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer, PK | Идентификатор |
| name | String | Название товара |
| category | String | Категория |
| min_price | Numeric(12,2) | Минимальная цена |
| max_price | Numeric(12,2) | Максимальная цена |
| rating | Float | Рейтинг |
| reviews_count | Integer | Количество отзывов |
| attributes | JSONB | Характеристики |
| images | JSONB | Изображения |
| sellers_count | Integer | Количество продавцов |
| source_url | String | URL источника |
| source_product_id | String, UQ | ID товара на Kaspi |
| created_at | DateTime | Дата создания |
| updated_at | DateTime | Дата обновления |

**offers**
| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer, PK | Идентификатор |
| product_id | Integer, FK | Связь с products |
| seller | String | Название продавца |
| price | Numeric(12,2) | Цена |

## 🔗 API Эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/parse` | Парсинг URL из `seed.json` |
| POST | `/parse/url` | Парсинг по переданному URL (`{"url": "..."}`) |
| GET | `/health` | Health check |

## 🔄 Обновления данных
- Интервал: 15 минут (переключается переменной `SCHEDULER_ENABLED=true`).
- Обновляются: поля продукта и офферы (upsert по `source_product_id`).

## 📝 Пример логов
```json
{"time": "2025-10-05T12:00:01", "level": "info", "event": "fetch_product", "url": "..."}
```

## ✅ Что сделано
- [x] Асинхронный парсинг товара (httpx + BeautifulSoup)
- [x] Асинхронная работа с БД (AsyncSession + asyncpg)
- [x] Сохранение в PostgreSQL (upsert)
- [x] Экспорт в JSON
- [x] REST API (FastAPI)
- [x] Логирование (structlog, JSON)
- [x] Docker + Docker Compose
- [x] Alembic миграции
- [x] Автообновление (APScheduler)

## 📄 Дополнительно
- Возможные улучшения: устойчивые селекторы для Kaspi, кэширование, хранение истории цен.
