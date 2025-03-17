# Visitor Management System (VMS)

## 📌 Project Overview
The **Visitor Management System (VMS)** is a web-based application built with Django that facilitates the registration, authentication, and tracking of visitors, employees, and administrators. It also manages assets and generates reports.

---

## 🏗️ Features
- User authentication (Admin, Employee, Visitor)
- Visitor registration and pre-registration
- Asset management (assigning and tracking)
- Secure login & registration with password validation
- Dashboard for reports and analytics
- Filtering system for visitors and assets
- Company and job listing with search & filters
- Role-based access control

---

## 🛠️ Tech Stack
- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (default), can be replaced with PostgreSQL/MySQL
- **Authentication**: Django's built-in authentication system

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository
```sh
 git clone https://github.com/Jeezlouis/Vistor-management-system.git
 cd Vistor-management-system
```

### 2️⃣ Create & Activate a Virtual Environment
```sh
# For Windows
python -m venv venv
venv\Scripts\activate

# For Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 4️⃣ Apply Migrations & Run Server
```sh
python manage.py migrate
python manage.py runserver
```

Now open **http://127.0.0.1:8000/** in your browser! 🎉

---

## 📂 Project Structure
```plaintext
VMS/
│── vms/                   # Django project directory
│   ├── settings.py         # Django settings (configure DB, static files, etc.)
│   ├── urls.py             # Routes and URL configurations
│   ├── wsgi.py             # Entry point for WSGI applications
│
│── apps/
│   ├── authentication/     # Handles user authentication (login, register, roles)
│   ├── visitors/           # Visitor registration and management
│   ├── assets/             # Asset management system
│   ├── reports/            # Reports and analytics
│
│── static/                 # Static files (CSS, JS, Images)
│── templates/              # HTML templates for views
│── media/                  # Uploaded images/files
│── manage.py               # Django management script
│── requirements.txt        # Project dependencies
│── README.md               # Documentation
```

---

## 🔐 User Roles & Permissions
| Role       | Permissions |
|------------|--------------------------------------------------|
| **Admin**  | Full access: Manage users, assets, reports, etc. |
| **Employee** | Can check in visitors, manage assets |
| **Visitor** | Can register, check status |

---

## 🔑 Authentication & Password Policy
- Password must be **at least 8 characters** long.
- Must contain **at least one uppercase letter**.
- Must be **alphanumeric** (include at least one number).

---

## 📜 API Endpoints (If Applicable)
| Endpoint | Method | Description |
|----------|--------|--------------------------------|
| `/login/` | POST | User login |
| `/register/` | POST | User registration |
| `/visitor/register/` | POST | Visitor pre-registration |
| `/assets/` | GET | Retrieve all assets |
| `/reports/` | GET | View reports |

---

## 🛠️ Deployment (For Production)
### 1️⃣ Collect Static Files
```sh
python manage.py collectstatic
```

### 2️⃣ Setup Gunicorn & Nginx (For Linux Server)
```sh
pip install gunicorn
```

Then configure **Gunicorn + Nginx** for deployment.

---

## 📜 License
This project is **MIT licensed**.

---

## 🤝 Contributing
1. Fork the repository 🍴
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -m 'Added new feature'`)
4. Push to your branch (`git push origin feature-branch`)
5. Submit a Pull Request ✅

---

## 📧 Contact
For questions or suggestions, reach out to **your-email@example.com** or open an issue on GitHub.

---

Happy Coding! 🎉

