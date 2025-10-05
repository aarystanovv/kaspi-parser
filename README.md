# Тестовое задание: Парсер Kaspi магазина

## 📌 Описание проекта
Сервис на FastAPI парсит карточку товара Kaspi и сохраняет данные:
- что парсит: название, категория, мин/макс цена, рейтинг, отзывы, (опц.) характеристики, изображения, количество продавцов, офферы
- куда сохраняет: PostgreSQL (таблицы `products`, `offers`), JSON (`export/product.json`, `export/offers.jsonl`)
- дополнительно: автообновление (15 минут), JSON-логирование, Docker, Alembic миграции

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
Создайте `.env` по примеру `.env.example`:
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
- id
- name
- category
- min_price
- max_price
- rating
- reviews_count
- attributes (JSON)
- images (JSON)
- sellers_count

**offers**
- id
- product_id
- seller
- price

## 🔄 Обновления данных
- Интервал: 15 минут (переключается переменной `SCHEDULER_ENABLED=true`).
- Обновляются: поля продукта и офферы (простая синхронизация).

## 📝 Пример логов
```json
{"time": "2025-10-05T12:00:01", "level": "info", "event": "fetch_product", "url": "..."}
```

## ✅ Что сделано
- [x] Парсинг товара
- [x] Сохранение в PostgreSQL
- [x] Экспорт в JSON
- [x] Логирование (JSON)
- [x] Docker
- [x] Alembic миграции

## 📄 Дополнительно
- Возможные улучшения: устойчивые селекторы для Kaspi, кэширование, хранение истории цен.
