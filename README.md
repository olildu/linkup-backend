<p align="center">
  <img src="https://raw.githubusercontent.com/olildu/linkup-frontend/refs/heads/main/assets/images/app_logo/app_logo_transparent.png" 
       alt="LinkUp Logo" 
       width="180">
</p>

# 🚀 LinkUp: The Backend Engine

A high-performance, asynchronous REST and WebSocket API built with **FastAPI**. This backend powers the LinkUp ecosystem with real-time matching, secure authentication, and scalable messaging infrastructure.

<p align="center">
  <a href="https://x.com/olildu">
    <img src="https://img.shields.io/twitter/follow/olildu.svg?style=social&label=Follow" alt="Twitter">
  </a>
  &nbsp;&nbsp;
  <a href="https://www.linkedin.com/in/ebinsanthosh/">
    <img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin&logoColor=white" alt="LinkedIn">
  </a>
</p>

## 🌟 Project Highlights & Technical Differentiators

This project demonstrates expertise in asynchronous Python development, complex database orchestration, and real-time event-driven architecture.

| Feature | Technical Implementation | Engineering Value Demonstrated |
| :--- | :--- | :--- |
| **Asynchronous Core** | **FastAPI** + **AsyncPG** connection pooling | High-concurrency handling, non-blocking I/O, optimized throughput |
| **Real-Time Events** | **WebSockets** with polymorphic event validation via **TypeAdapter** | Robust real-time messaging, typing indicators, and read receipts |
| **Low-Latency Caching** | **Redis** integration for state management | Reduced database load, fast access to transient session data |
| **Task Orchestration** | **APScheduler** for cron-based background jobs | Reliable execution of periodic events (e.g., "Meet at 8" lobby) |

## 🧱 Architecture Overview: Asynchronous Micro-services

The backend is structured to handle high-frequency swiping and messaging through a modern, modular design.

### **API Entry & Middleware (`app/main.py`)**
- Orchestrates the app lifecycle, managing the database pool and background schedulers.
- Implements versioned routing (`/api/v1`) for seamless future updates.
- Serves static assets for legal and safety documentation.

### **Websocket Layer (`app/routes/chats`, `app/routes/matches`)**
- **Chat Socket** — Manages persistent bi-directional connections for messaging, supporting text content, media metadata, and delivery states.
- **Lobby Socket** — Powers the synchronous matchmaking lobby with automated waiting periods.

### **Utility & Logic Layer (`app/utilities`)**
- **Security** — Implements JWT-based authentication and secure password hashing.
- **Data Validation** — Leverages Pydantic for strict schema enforcement across all REST and WebSocket payloads.

## ⚙️ Core Modules & Components

| Module | Purpose | Key Files |
| :--- | :--- | :--- |
| **Auth Service** | Multi-stage registration and secure login | `auth_endpoints.py`, `auth_utilities.py` |
| **Match Engine** | Location-based filtering and swipe logic | `swipe_endpoint.py`, `matches_utilities.py` |
| **Chat Service** | Persistence and delivery of real-time interactions | `chat_websocket_endpoints.py`, `chat_utilities.py` |
| **Controller Layer** | Interface for PostgreSQL, Redis, and Cloud Storage | `db_controller.py`, `redis_controller.py` |

## 🛠️ Development Setup

Requires **Python 3.11+**.

### **1. Installation**
```bash
  git clone https://github.com/olildu/linkup-backend.git
  cd linkup-backend
  pip install -r requirements.txt
```

### **2. Configuration**
```bash
  DB_HOST=localhost
  DB_NAME=linkup
  REDIS_URL=redis://localhost:6379
  SECRET_KEY=your_secret_key
```

### **3. Running the Server**
```bash
  uvicorn app.main:app --reload
```

## 📱 Ecosystem Logic

LinkUp Backend is designed to maintain **high availability** and **data integrity** through the following mechanisms:

- **Connection Resilience:**  
  WebSocket connections handle disconnects gracefully, ensuring no messages are lost during network transitions or temporary network failures.

- **Automated Maintenance:**  
  APScheduler manages the daily lifecycle of matching events, ensuring consistent engagement and timely updates for the user base.

- **Data Protection:**  
  All user interactions are strictly validated using Pydantic models before reaching the persistence layer, preventing malformed or unsafe data from being stored.
