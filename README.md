🏘️ Smart Village Backend (Django)

This is the backend service for the Smart Village Platform, a community-driven digital solution designed to connect residents, visitors, local leaders, and public services within a modern digital ecosystem.

It powers the Smart Village Frontend by providing secure APIs, data storage, authentication, and moderation features for all users and roles.

🚀 Core Features (MVP Scope)
🧍‍♂️ Resident & Visitor Management

Resident registration with phone number verification (OTP)

Visitor profiles linked to residents

Role-based access (Resident, Sector Leader, District Admin)

Account approval by moderators

📰 Community News & Announcements

Create, update, and publish posts (text + image uploads)

Moderation workflow before publication

API for comments and likes

Public feed endpoint for frontend

📅 Events & Calendar

CRUD endpoints for community events

Filter by sector, category, or date

Integration-ready for calendar UI

☎️ Contacts Directory

APIs for storing and retrieving essential numbers (leaders, health workers, etc.)

Supports offline caching for frontend PWA

💬 Suggestion Box / Feedback

Anonymous or identified feedback submission

Moderation queue before publication

Review status tracking

💪 Skills & Volunteering

API for residents to register their skills

Admins can post volunteer opportunities

Matching system between volunteers and community needs

🚨 Incident Reporting & Alerts

Residents can report incidents with photo uploads and geolocation

Admins verify and push alerts to all users

Integration with push notification service

🌐 Multilingual & Localization Support

Language fields: Kinyarwanda, English, French

Django internationalization (i18n) support

🛠 Tech Stack
Category	Technology
Backend Framework	Django 5+
API Framework	Django REST Framework (DRF)
Database	MySQL 8.0
Authentication	JWT (SimpleJWT)
Email Verification	Django Email + SMTP
File Storage	Django Media / Cloud (optional)
Documentation	DRF Spectacular / Swagger UI
Deployment	Gunicorn + Nginx / Docker (optional)
📦 Installation & Setup
1️⃣ Clone Repository
git clone https://github.com/Manzp111/smartville-backend.git
cd smartville-backend

2️⃣ Create Virtual Environment
python -m venv env
env\Scripts\activate  # On Windows
source env/bin/activate  # On Linux/macOS

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Setup Environment Variables

Create a .env file in the project root:

SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=smartvillage
DB_USER=Ngilbert
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=True

5️⃣ Apply Migrations
python manage.py makemigrations
python manage.py migrate

6️⃣ Create Superuser
python manage.py createsuperuser

7️⃣ Run Server
python manage.py runserver


The backend runs on 👉 http://127.0.0.1:8000

🌐 API Documentation

After running the server, open:

Swagger UI: http://127.0.0.1:8000/api/schema/swagger-ui/

ReDoc: http://127.0.0.1:8000/api/schema/redoc/

🗂️ Folder Structure
smartville-backend/
│
├── smartvillage/          # Project root (settings, URLs)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── accounts/          # User & role management
│   ├── news/              # Posts, announcements
│   ├── events/            # Events calendar
│   ├── feedback/          # Suggestions & reports
│   ├── volunteers/        # Skills & opportunities
│   ├── alerts/            # Incidents & notifications
│   └── contacts/          # Essential contacts
│
├── media/                 # Uploaded images/files
├── static/                # Static files
├── requirements.txt
└── manage.py

🔒 Authentication & Authorization

JWT Authentication using djangorestframework-simplejwt

Role-based access control:

Resident: Can view & submit requests

Sector Leader: Can approve within assigned sector

District Admin: Full control of all sectors

🧩 Integration with Frontend
Frontend Route	Backend Endpoint
/register	/api/auth/register/
/login	/api/auth/login/
/feed	/api/news/
/events	/api/events/
/contacts	/api/contacts/
/feedback	/api/feedback/
/alerts	/api/alerts/

Frontend repo: Smart Village Frontend

🧱 Deployment
Build Static Files
python manage.py collectstatic

Production Stack

Web Server: Nginx

App Server: Gunicorn

Database: MySQL / PostgreSQL

OS: Ubuntu / Debian

Optional: Docker container setup

🔮 Future Enhancements (Post-MVP)

Integration with mobile app (Flutter)

Real-time updates via WebSockets (Django Channels)

Advanced analytics for admins

SMS gateway for non-smartphone users

AI-based community insights

👥 Contributors
Name	Role	GitHub
Gilbert Manzi	Backend Developer	@Manzp111

Solvit Africa Training Center	Technical Partner	@Solvit-Africa-Training-Center
🪪 License

This project is licensed under the MIT License.
You are free to use, modify, and distribute with attribution.
