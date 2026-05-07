# NepSewa Project Context

## What is this project
- Semester final project by Samrajya and his friend (Utsav Bhandari)
- A home services platform for Nepal — customers book service providers (plumber, cleaner, electrician, etc.)
- GitHub repo: https://github.com/utsavbha/nepsewafinalsem

## Tech Stack
- Backend: Python Flask
- Database: MySQL (via XAMPP on Samrajya's machine)
- Frontend: HTML, CSS, JavaScript
- Payments: eSewa integration
- Auth: Session-based

## Project Structure
- Main files are in `nepsewafinalsem/` (root level after friend's v2.0 restructure)
- `main.py` — main Flask app (1970+ lines)
- `run_server.py` — startup script with DB checks
- `templates/` — all HTML pages
- `static/` — CSS, JS, images

## How to Run
1. Open XAMPP Control Panel and start MySQL
2. In terminal, go to `nepsewafinalsem/` folder
3. Run: `py run_server.py`
4. Open browser: http://127.0.0.1:8001

## Important Notes
- Use `py` command (not `python` or `python3`) — Python 3.13 installed via py launcher
- XAMPP MySQL runs with no password (root user, empty password)
- `main.py` DB config has `password=""` (XAMPP default) — friend's version has `password="nepsewa123"`
- This password difference is intentional and machine-specific, do NOT push it to git
- Database name: `nepsewa`
- Server runs on port 8001

## Key URLs
- Home: http://127.0.0.1:8001
- Services: http://127.0.0.1:8001/services
- Login: http://127.0.0.1:8001/login
- Provider Login: http://127.0.0.1:8001/provider/login
- Admin Panel: http://127.0.0.1:8001/admin (password: admin123)

## Git Info
- Local branch: main
- Remote: origin/main
- Only difference from remote: the DB password line in main.py (intentional, machine-specific)
- To pull friend's changes: `git -C nepsewafinalsem pull` then re-apply empty password in main.py
