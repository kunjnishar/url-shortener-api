# Shorten Engine — URL Shortener & Analytics API

A high-performance, production-ready URL shortening and click-tracking microservice built with Python and Django REST Framework.

🌐 **Live Demo:** [https://url-shortener-api-fexe.onrender.com](https://url-shortener-api-fexe.onrender.com)

---

## ⚡ Key Features

- **Base62 Slug Generation:** Encodes auto-incrementing record IDs into compact, collision-free URL slugs ($O(1)$ lookup time).
- **Atomic Concurrency Tracking:** Leverages database `F()` expressions to handle high-frequency redirect click counting without race conditions.
- **RESTful Endpoints:** Complete API layer for link encoding, retrieval, and granular click analytics.
- **Modern Responsive Client:** Vanilla JavaScript interface with asynchronous state management and real-time click polling.
- **Production Hardening:** Managed environment configuration (`SITE_DOMAIN`, `SECRET_KEY`, `DEBUG`), WhiteNoise static caching, and WSGI deployment via Gunicorn on Render.

---

## 🛠️ Tech Stack

- **Backend:** Python, Django 5, Django REST Framework
- **Static & Server:** WhiteNoise, Gunicorn
- **Database:** SQLite (Local) / PostgreSQL-ready (Engine agnostic)
- **Deployment:** Render PaaS, GitHub Actions / Auto-deploy CI/CD

---

## 🔌 API Endpoints

| Method | Endpoint | Description | Payload / Params |
|---|---|---|---|
| `POST` | `/api/shorten/` | Generates a new short slug | `{"original_url": "https://example.com"}` |
| `GET` | `/r/<slug>/` | Redirects to original URL | Increments click count atomically |
| `GET` | `/api/analytics/<slug>/` | Retrieves click count & metadata | Returns JSON analytics |

---

## 🚀 Local Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/kunjnishar/url-shortener-api.git](https://github.com/kunjnishar/url-shortener-api.git)
   cd url-shortener-api