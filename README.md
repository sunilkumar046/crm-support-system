# CRM Support System

A backend CRM Support System built with **Python, FastAPI, SQLAlchemy, PostgreSQL, and Alembic**. The application provides APIs for managing customers, support tickets, ticket responses, categories, notifications, attachments, SLA policies, audit logs, and dashboard information.

## 🚀 Features

* User registration and authentication
* JWT-based authentication and authorization
* Customer management
* Support ticket management
* Ticket categories
* Ticket responses
* File attachment management
* Notification management
* SLA policy and SLA management
* Audit logging
* Dashboard APIs
* PostgreSQL database integration
* SQLAlchemy ORM
* Alembic database migrations
* RESTful API architecture
* Background service support
* Swagger/OpenAPI API documentation

## 🛠️ Tech Stack

* **Language:** Python
* **Framework:** FastAPI
* **ORM:** SQLAlchemy
* **Database:** PostgreSQL
* **Database Migration:** Alembic
* **Authentication:** JWT
* **Password Hashing:** bcrypt
* **Server:** Uvicorn
* **Validation:** Pydantic
* **API Documentation:** Swagger UI / OpenAPI

## 📁 Project Structure

```text
crm_support_system/
│
├── app/
│   ├── core/
│   │   ├── enums.py
│   │   └── security.py
│   │
│   ├── database/
│   │   └── database.py
│   │
│   ├── models/
│   │   ├── attachment.py
│   │   ├── audit_log.py
│   │   ├── category.py
│   │   ├── customer.py
│   │   ├── notification.py
│   │   ├── sla_policy.py
│   │   ├── ticket.py
│   │   ├── ticket_response.py
│   │   └── user.py
│   │
│   ├── repositories/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   └── main.py
│
├── alembic/
│   └── versions/
│
├── alembic.ini
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd crm_support_system
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/crm_support
SECRET_KEY=your-secret-key
```

> Never commit your `.env` file or other credentials to GitHub.

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## 📚 API Documentation

After starting the application, open:

```text
http://127.0.0.1:8000/docs
```

Swagger UI provides an interactive interface for testing the available API endpoints.

Alternative OpenAPI documentation:

```text
http://127.0.0.1:8000/redoc
```

## 🔐 Authentication

The system uses JWT-based authentication.

Typical authentication flow:

1. Register a user.
2. Login with valid credentials.
3. Receive an authentication token.
4. Use the token to access protected APIs.

## 🗄️ Database

The application uses **PostgreSQL** with **SQLAlchemy** for database operations.

Alembic is used to manage database schema changes and migrations.

Run:

```bash
alembic upgrade head
```

to apply the latest database migrations.

## 🔄 Main Modules

| Module         | Purpose                                    |
| -------------- | ------------------------------------------ |
| Authentication | User registration, login and authorization |
| Customers      | Customer information management            |
| Tickets        | Support ticket creation and management     |
| Categories     | Ticket categorization                      |
| Responses      | Ticket response management                 |
| Notifications  | User notification management               |
| Attachments    | Ticket file attachments                    |
| SLA            | SLA policies and management                |
| Audit Logs     | Tracking system activities                 |
| Dashboard      | CRM support statistics and information     |

## 🧪 Testing APIs

The APIs can be tested using:

* Swagger UI
* Postman
* Any REST API client

Swagger:

```text
http://127.0.0.1:8000/docs
```

## 🔒 Security

Sensitive configuration should be stored in environment variables.

The following files should not be committed:

```text
.env
venv/
__pycache__/
*.pyc
```

## 👨‍💻 Author

**Sunil Kumar Vuravula**

## 📄 License

This project is intended for learning, development, and demonstration purposes.
