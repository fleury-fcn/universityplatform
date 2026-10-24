🇬🇧🇺🇸 English version · 🇫🇷 [Version française](README.fr.md) (full documentation)

# 🎓 ISTA — the student app of the Institute of Applied Statistics

A mobile-first web app that puts the whole **Institute of Applied Statistics (ISTA)**, University of
Burundi, in students' pockets. Inspired by *Lilu* (University of Lille), adapted to ISTA's reality:
entry-level Android phones, slow or unstable connections, low-cost hosting.

> ⚠️ Shipped data is **demo data** (shown with a "DEMO" badge). See
> [DONNEES_A_COMPLETER.md](DONNEES_A_COMPLETER.md) (in French) before going live.

## Features

- **Roles**: student, teacher, administration — access control on every route
- **News** with categories and promotion targeting · **in-app notifications** (+ optional web push)
- **Timetable** per promotion (day / week views), weekly sessions with one-off cancellations or moves
- **Courses & resources**: lecture notes, tutorials, past exams (secure upload / download)
- **Grades** per semester (entered and published by teachers, indicative weighted average)
- **Library**: catalogue, availability, reservations, optional digital copies
- **Campus**: places and rooms, uploaded campus maps, link to the phone's map app
- **Clubs**, student **tips** ("tuyaux") with moderation, internal **messaging** with attachments
- **FAQ assistant**: plain-language search over admin-written questions (accent- and typo-tolerant, works offline-friendly, no AI service)
- **Offline-ready PWA**: weekly timetable, news, campus and courses are pre-cached; downloaded files stay available
- **Lightweight**: no CDN, no web font, one stylesheet, one small script · light / dark theme
- **Languages**: French by default, i18n ready for English and Kirundi

## Quick start

```bash
git clone https://github.com/fleury-fcn/universityplatform.git
cd universityplatform
make dev          # venv + dependencies + SQLite + demo data + server on http://127.0.0.1:5001
make test         # test suite
```

Demo accounts (password `Demo-ISTA-2026`): `admin.demo`, `enseignant.demo`, `etudiant.demo`, `etudiante.demo`.

Production: `docker compose up -d --build` (PostgreSQL + gunicorn) behind an HTTPS proxy — see the
French README for configuration, deployment and backups.

**Stack**: Python 3.11+, Flask 3, SQLAlchemy 2, Alembic, Flask-Login, Flask-WTF, Flask-Babel,
PostgreSQL (SQLite in development), vanilla CSS/JS, service worker.

## 👤 Author

<img src="https://github.com/fleury-fcn.png" width="100" style="border-radius: 50%;" alt="Fleury Niyokwizera" />

**Fleury NIYOKWIZERA**
Master 1 in Applied Statistics and Decision-Making Computer Science – ISTA, University of Burundi
Currently pursuing a Master's in Data Modeling (Artificial Intelligence track) – University of Lille

[![GitHub](https://img.shields.io/badge/GitHub-fleury--fcn-181717?style=flat&logo=github&logoColor=white)](https://github.com/fleury-fcn)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Fleury_Niyokwizera-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/fleury-niyokwizera-2a9436291)
[![Email](https://img.shields.io/badge/Email-fleuryniyokwizera2021%40gmail.com-D14836?style=flat&logo=gmail&logoColor=white)](mailto:fleuryniyokwizera2021@gmail.com)
