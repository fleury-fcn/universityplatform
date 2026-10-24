# Contributing to OpenISTA

First off, thank you for considering contributing to **OpenISTA**! 🎓

This project started as a Master's capstone project — a full-featured university campus management platform built for ISTA, University of Burundi. It's now open for anyone who'd like to help improve it, whether you're a student, a developer learning Flask, or someone who's used a similar system and has ideas for improvement.

---

## 🙋 Ways to contribute

You don't need to be an expert developer to help. Here are several ways to get involved:

- **🐛 Report bugs** — Found something broken? Open an issue describing what happened and how to reproduce it.
- **💡 Suggest features** — Have an idea for a campus service the platform is missing? Open an issue to discuss it before starting work.
- **💻 Write code** — Fix bugs, build features, improve performance. See [Good first issues](#-good-first-issues) below.
- **📝 Improve documentation** — Clearer setup instructions, better code comments, or corrections to this file are all welcome.
- **🎨 Improve the UI** — The frontend is built with HTML/Jinja2 templates and could benefit from design polish.
- **🧪 Add tests** — Every feature has tests under `tests/`; new behaviour should come with new tests.

---

## 🛠️ Setting up your development environment

### Prerequisites
- Python 3.11+
- Git
- `make` (macOS / Linux) — Windows commands are in the [French README](README.fr.md)
- PostgreSQL is optional (SQLite is used by default in development)

### Steps

```bash
# 1. Fork this repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/universityplatform.git
cd universityplatform

# 2. Add the original repository as an upstream remote
git remote add upstream https://github.com/fleury-fcn/universityplatform.git

# 3. Install, create the SQLite database, load demo data and run
make dev

# 4. Run the tests (please add tests with every change)
make test
```

After changing a model: `flask --app run.py db migrate -m "short description"` then
`flask --app run.py db upgrade`, and commit the generated migration. User-facing text is written in
French and wrapped in `_()` so it can be translated (`make translations`).

You now have a working local copy of the platform. 🎉

---

## 🔄 Making a contribution

1. **Create a branch** for your change, based on the latest `main`:
   ```bash
   git checkout main
   git pull upstream main
   git checkout -b feature/short-description
   ```

2. **Make your changes.** Keep commits focused — one logical change per commit when possible.

3. **Write clear commit messages**, following this convention where relevant:
   ```
   feat: add attendance tracking for teachers
   fix: correct grade calculation in evaluations module
   docs: clarify local setup instructions
   ```

4. **Test your changes locally** before opening a pull request. Make sure the app still runs (`python run.py`) and the feature/fix behaves as expected.

5. **Push your branch and open a Pull Request:**
   ```bash
   git push origin feature/short-description
   ```
   Then open a PR on GitHub against the `main` branch of this repository. Describe what your change does and why.

6. **Respond to review feedback.** A maintainer will review your PR and may suggest changes — this is a normal part of the process, not a rejection.

---

## 🎯 Good first issues

New to the project? Look for issues labeled [`good first issue`](../../labels/good%20first%20issue) — these are scoped to be approachable without deep familiarity with the codebase.

Don't see one that fits? Feel free to open an issue proposing a small improvement (a UI fix, a missing form validation, a documentation gap) and mention you'd like to work on it.

---

## 🧭 Project structure

For an overview of how the codebase is organized (one module per feature under `app/`), see the [French README](README.fr.md#-architecture).

---

## 💬 Questions?

If anything is unclear, open an issue with the `question` label, or reach out via [fleuryniyokwizera2021@gmail.com](mailto:fleuryniyokwizera2021@gmail.com).

---

## 📜 Code of Conduct

Be respectful, be constructive, and remember there's a person on the other side of every issue and pull request. We want this to be a welcoming space for contributors of all backgrounds and experience levels.

---

Thank you again for helping improve a tool built to serve real students and teachers. 🙏
