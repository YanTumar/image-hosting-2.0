# 🖼️ Web Image Hosting Service

Простий та швидкий веб-сервіс для завантаження зображень та отримання прямих посилань.

---

## 🛠️ Технології

- **Backend:** Python 3.12 (HTTP server, Pillow) 🐍
- **Static Proxy:** Nginx ⚡
- **Containerization:** Docker & Docker Compose 🐳

---

## 📋 Основні маршрути API

- `GET /` — Головна сторінка сервісу 🌐
- `POST /upload` — Завантаження зображення (`.jpg`, `.png`, `.gif` до 5 МБ) 📤
- `GET /images/<filename>` — Отримання та перегляд зображення 🖼️

---

## 🚀 Запуск проєкту

Для запуску проєкту виконайте команду:

```bash
docker compose up --build