# Auth Service

## 🔐 Authorization microservice with FastAPI, PostgreSQL, JWT, and Docker

This service handles secure authentication and role-based access control for your web application. Includes
production-grade practices: refresh tokens, Swagger BasicAuth, centralized logging, backups, and rate-limiting.

---

## 🧰 Technologies

- **FastAPI** + **Pydantic**
- **PostgreSQL** + SQLAlchemy ORM
- **Docker / Compose**
- **JWT** (access + refresh)
- **Rate limiting** with SlowAPI
- **Swagger UI** protected by HTTP Basic Auth
- **Centralized logging** to PostgreSQL
- **Auto backups** using `pg_dump`

---

## 🚀 Getting Started

### 1. Clone repository and setup environment

```bash
git clone https://github.com/dym-dino/AuthService.git
cd AuthService
cp .env.example .env
```

### 2. Run with Docker

```bash
docker-compose up --build
```

### 3. Access API

- Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- Requires HTTP Basic Auth from `.env`

---

## 🔐 Main endpoints

| Method | Endpoint                     | Description                |
|--------|------------------------------|----------------------------|
| POST   | `/api/v1/token`              | Get access + refresh token |
| POST   | `/api/v1/refresh`            | Get new access token       |
| GET    | `/api/v1/me`                 | Get user info from token   |
| POST   | `/api/v1/admin/create_admin` | Create new admin/operator  |
| DELETE | `/api/v1/admin/remove_admin` | Remove admin/operator      |

---

## 🧪 Testing

Use Swagger or Postman to test each endpoint. Tokens are passed via `Authorization: Bearer <token>`.

Run tests with:

```bash
pytest -v
```

---

## 🧾 License

MIT License. See [LICENSE](LICENSE) file.

---

## 📌 ToDo (for future improvements)

- [ ] Add email verification / password reset flow
- [ ] Move logs to external log aggregator