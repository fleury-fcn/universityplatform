🇬🇧 English version · 🇫🇷 [Version française](README.fr.md)

# 🎓 OpenISTA – University Campus Management Platform

**OpenISTA** is a full-featured web platform for university campus management, developed for the **Institute of Applied Statistics (ISTA)**, Center of Excellence at the **University of Burundi**, as the capstone project for a **Master 1 in Applied Statistics and Decision-Making Computer Science**.

The goal: design and build, end-to-end, a system capable of managing the full range of administrative and academic services of a university campus — students, faculty, courses, library, student life, and internal communication.

---

## 📌 Academic context

This project was developed individually to apply skills learned across several courses of the Master's program:

- **Databases** – relational design, modeling, migrations
- **Advanced Programming (Python / Flask)** – back-end architecture, business logic
- **Software Engineering** – code structuring, project management, best practices
- Other courses from the decision-making computer science core curriculum

---

## ✨ Key features

The platform covers the full lifecycle of university campus operations:

### 👨‍🎓 Academic management
- Student record management
- Faculty management and assignments
- Course and program management

### 📚 Library
- Catalog and management of available books
- Loan tracking (seeded via `init_books.py`)

### 🏛️ Campus life
- Management of student clubs and associations (`init_clubs.py`)
- Space for students to share tips/resources with each other

### 💬 Communication
- Internal messaging system with attachment support
- User-to-user notifications

---

## 🛠️ Tech stack

| Component | Technology |
|---|---|
| Back-end | Python / Flask |
| Database | PostgreSQL |
| Migrations | Flask-Migrate / Alembic |
| Front-end | HTML, CSS, Jinja2 |
| Dependency management | pip / requirements.txt |

---

## 📁 Project structure

```
universityplatform/
├── app/                        # Core application (routes, models, business logic)
├── migrations/                 # Database migration history
├── static/uploads/messages/    # Internal messaging attachments
├── work/                       # Additional modules
├── init_books.py               # Initial seed data – library
├── init_clubs.py                # Initial seed data – clubs
├── init_courses.py             # Initial seed data – courses
├── init_tuyaux.py              # Initial seed data – student resources
├── run.py                      # Application entry point
└── requirements.txt             # Python dependencies
```

---

## 🚀 Local installation and setup

```bash
# 1. Clone the repository
git clone https://github.com/fleury-fcn/universityplatform.git
cd universityplatform

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env          # then fill in your own PostgreSQL credentials

# 5. Initialize the database
flask db upgrade

# 6. (Optional) Seed the database with demo data
python init_books.py
python init_clubs.py
python init_courses.py
python init_tuyaux.py

# 7. Run the application
python run.py
```

---

## 🎯 Skills demonstrated

- Relational database design and modeling
- Back-end development with Flask (routing, ORM, authentication)
- Database schema migration management
- Modular software architecture
- Independent project management, from requirements to delivery

---

## 👤 Author

<img src="https://github.com/fleury-fcn.png" width="100" style="border-radius: 50%;" alt="Fleury Niyokwizera" />

**Fleury NIYOKWIZERA**
Master 1 in Applied Statistics and Decision-Making Computer Science – ISTA, University of Burundi
Currently pursuing a Master's in Data Modeling (Artificial Intelligence track) – University of Lille

[![GitHub](https://img.shields.io/badge/GitHub-fleury--fcn-181717?style=flat&logo=github&logoColor=white)](https://github.com/fleury-fcn)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Fleury_Niyokwizera-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/fleury-niyokwizera-2a9436291)
[![Email](https://img.shields.io/badge/Email-fleuryniyokwizera2021%40gmail.com-D14836?style=flat&logo=gmail&logoColor=white)](mailto:fleuryniyokwizera2021@gmail.com)
