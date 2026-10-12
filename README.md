# Product Expiry Alert Management System

A security-focused inventory control web application designed to track product lifecycles, flag expiring stock in real-time, and automate email alerts. Built as an academic capstone project to demonstrate a complete, decoupled architecture with role-based access control.

---

## Technical Architecture

The system uses a clean separation of concerns between a Python backend API and a responsive single-page dashboard frontend.

* **Backend**: Python (Flask) providing a RESTful API.
* **Database & ORM**: SQLite managed via SQLAlchemy, handling relational data for users and inventory items.
* **Security**: Password hashing with `Flask-Bcrypt` and stateless user sessions secured via JSON Web Tokens (JWT).
* **Automation & Alerts**: Background inventory checks executed via `Flask-APScheduler`, paired with `Flask-Mail` for dispatching automated email notifications when stock reaches critical expiration thresholds.
* **Frontend**: Single-page dashboard built with HTML5, Tailwind CSS for styling, and Vanilla JavaScript for asynchronous API communication and UI state management.

---

## Core Features

* **Role-Based Access Control (RBAC)**: 
  * **Admin**: Full access to manage inventory, create/edit product records, and delete items.
  * **Manager**: Can add and update product inventory.
  * **Clerk**: Read-only view access to monitor stock status.
* **Dynamic Status Tracking**: Products are automatically evaluated in real-time and categorized as *Fresh*, *Expiring Soon* ($\le 30$ days), or *Expired*.
* **Automated Expiry Checks**: A background scheduler runs daily tasks to scan the database and trigger notifications for compromised items.
* **Dual-Mode Dashboard**: Supports switching between a local mock data mode (for quick offline prototyping) and live interaction with the Flask REST API backend.
* **Export & Reporting**: Built-in CSV report generation for instant inventory auditing.

---

## Project Structure

```text
product-expiry-system/
│
├── app/
│   ├── models.py            # SQLAlchemy database models (User, Product)
│   ├── routes/              # Blueprint routes (Auth & Products)
│   ├── utils/               # Background tasks & scheduler logic
│   └── templates/           # Frontend dashboard (index.html)
│
├── instance/                # Local SQLite database storage
├── .gitignore               # Ignored runtime and environment files
├── config.py                # Application configuration settings
├── requirements.txt         # Python package dependencies
└── run.py                   # Application entry point
```

## Setup and Installation
Follow these steps to run the project locally on your machine:

1. Clone or Open the Repository
Navigate to your project directory in your terminal.

2. Set Up a Virtual Environment
```bash
python -m venv venv
# Activate on Windows:
venv\Scripts\activate
# Activate on macOS/Linux:
source venv/bin/activate
```
3. Install dependencies 
```bash 
pip install -r requirements.txt 
```
4. Configure Environment Variables
```text
SECRET_KEY=your_secret_key_here
MAIL_SERVER=smtp.googlemail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_email_app_password
```
5. Run the Application
```bash
python run.py
```
Open your browser and navigate to http://localhost:5000. You can toggle to the Live API mode via the navigation bar to register an account and interact with the database.

# 🔒 Security Practices Implemented

Password Hashing: Plaintext passwords are never stored; hashing is enforced using Flask-Bcrypt salt rounds.

Stateless Authentication: Protected endpoints validate cryptographic JSON Web Tokens (JWT) attached via request headers.

Least Privilege Principle: UI and API routes evaluate user roles before authorizing mutations (POST, PUT, DELETE).

# 📄 License

This project was developed as a Computer Science final year project.
