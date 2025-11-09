# Frame1 Project

Проект состоит из FastAPI backend, Next.js frontend и PostgreSQL базы данных.

## Структура проекта

```
frame1/
├── backend/          # FastAPI приложение
├── frontend/         # Next.js приложение
└── docker-compose.yml
```

## Переменные окружения для PostgreSQL

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=frame1_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

## URL для подключения к базе данных

**Внутри Docker контейнеров:**
```
postgresql://postgres:postgres@db:5432/frame1_db
```

**С локального компьютера (вне Docker):**
```
postgresql://postgres:postgres@localhost:5432/frame1_db
```

## Запуск всего проекта

Запустить все сервисы (frontend, backend, database):

```bash
docker-compose up --build
```

Запустить в фоновом режиме:

```bash
docker-compose up -d --build
```

Остановить все сервисы:

```bash
docker-compose down
```

## Запуск отдельных сервисов

### Запустить только базу данных

```bash
docker-compose up db
```

### Запустить только backend

```bash
docker-compose up db backend
```

### Запустить только frontend

```bash
docker-compose up frontend
```

### Запустить backend и базу данных (без frontend)

```bash
docker-compose up db backend
```

## Доступ к сервисам

После запуска сервисы будут доступны по адресам:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Backend API Docs:** http://localhost:8000/docs
- **PostgreSQL:** localhost:5432

## Локальная разработка (без Docker)

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### База данных

Для локальной разработки нужно запустить только PostgreSQL:

```bash
docker-compose up db
```

## Полезные команды

Просмотр логов:
```bash
docker-compose logs -f
```

Просмотр логов конкретного сервиса:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

Пересобрать контейнеры:
```bash
docker-compose build
```

Удалить все контейнеры и volumes:
```bash
docker-compose down -v
```
