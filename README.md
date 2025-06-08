# 🪹 Numismatist Collection Manager

[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/frontend-Vue_3-blueviolet)](https://vuejs.org/)

## 🌟 Project Overview

This is a full-stack application built for **numismatists** to manage, categorize, and share collections of **coins and banknotes**. It includes:

* 🔐 Auth system with subscription tiers
* 📆 RESTful API using FastAPI
* 🌐 Web frontend using Vue.js
* 📁 Exportable reports (CSV/PDF)
* 🔗 Public sharing of collections

---

## ⚙️ Architecture

The platform consists of several decoupled components:

* **API Service** – FastAPI backend serving JSON REST endpoints.
* **Frontend** – Vue 3-based SPA with Composition API + Pinia.
* **Database** – PostgreSQL storing users, items, and collections.
* **Authentication** – JWT-based auth powered by `fastapi-users`.
* **Report Generator** – CSV and PDF export (Advanced & Pro).
* **Dockerized Environment** – Full development setup via Docker.

---

## ✨ Features

### 👤 User Management

* Sign up, login, logout, password reset
* Email verification (optional)
* User profile page showing subscription tier

### 💳 Subscription Tiers

| Tier     | Features                              |
|----------|---------------------------------------|
| Free     | Up to 100 items                       |
| Advanced | 500 items + report export             |
| Pro      | Unlimited items + report export       |

> 🔒 Tier enforcement is handled on both backend and frontend.

### 🪙 Item Management

* CRUD operations for coins and banknotes
* Fields: type, year, denomination, grade, country, material, etc.
* Paginated and filterable views
* Warnings when nearing limits

### 📚 Collections & Sharing

* Group items into named collections
* Optional public sharing via `/shared/{slug}`

### 📄 Report Export

* Available to Advanced/Pro users
* `/reports/export` endpoint (CSV/PDF)
* Download directly from the frontend

---

## 🚀 Quick Start

### 🔧 Prerequisites

* Docker & Docker Compose
* Make (optional)

### 🏁 Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/numismatist-app.git
   cd numismatist-app
   ```

2. **Run the application**

   ```bash
   make setup
   ```

3. **Access the services**

   * API Docs: [http://localhost:8000/docs](http://localhost:8099/docs)

---

## 🔐 Configuration Notes

### ✅ Setting up Auth

* JWT-based auth using `fastapi-users`
* All routes requiring auth are protected
* Tokens are stored and refreshed via the frontend Pinia store

### 🔑 Secrets Setup

To securely enable password reset and email verification features, you must set the following environment variables:

* `ACCESS_TOKEN__RESET_PASSWORD_TOKEN_SECRET`
* `ACCESS_TOKEN__VERIFICATION_TOKEN_SECRET`

You can generate secure values for them using the following Python one-liner:

```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(64))'
```

Add the generated secrets to your `.env` file or your deployment environment.


## 🧪 License

This project is licensed under the MIT License.
