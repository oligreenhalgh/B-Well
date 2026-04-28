# B-Well

A daily wellbeing tracking web app for University of Birmingham students. Students log short daily check-ins across five categories (stress level, sleep quality, social life, academic engagement, and activity level) and view their trends over time.

<p align="center">
  <img src="app/static/image/BwellLogolong.svg" alt="B-Well logo" width="400">
</p>

<p align="center">
  <em>Daily wellbeing tracking for University of Birmingham students.</em>
</p>

---

## Preview

<p align="center">
  <img src="app/static/image/Screenshot 2026-04-28 065602.png" alt="B-Well home page" width="700">
</p>

## Features

- University-email-gated registration (`@student.bham.ac.uk` / `@bham.ac.uk`)
- Secure login/logout via Flask-Login with hashed passwords
- Daily wellbeing check-in (5 metrics on a 1–5 scale + optional notes)
- Resource recommendation logic
- Daily check-in reminders by in-app notification (via APScheduler)
- Historical visualisation with Chart.js; switch between metrics to view trends
- Admin dashboard to manage wellbeing resources (Create, Read, Update, Delete)
- Persistent SQLite storage

## Tech stack

| Layer | Library |
|---|---|
| Web framework | Flask |
| ORM | Flask-SQLAlchemy |
| Auth | Flask-Login |
| Forms | Flask-WTF / WTForms |
| Background jobs | APScheduler |
| Database | SQLite |
| Charts | Chart.js (CDN) |

## Project structure

```
B-Well/
├── app/
│   ├── __init__.py       # Flask app, DB, login manager, scheduler startup
│   ├── models.py         # User, WellbeingResponse, Notification, Resource
│   ├── forms.py          # Registration, Login, Wellbeing forms + validators
│   ├── routes.py         # All route handlers
│   ├── scheduler.py      # Daily notification background job
│   └── templates/        # Jinja2 templates
├── config.py             # Flask configuration
├── requirements.txt      # Python dependencies
├── setup.py              # Populate database with dummy data
└── app.db                # SQLite database
```

## Getting started

### Prerequisites
- Python 3.11+
- `pip`

### Installation

```bash
# 1. Clone the repo
git clone <repo-url>
cd B-Well

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration & Database Setup

Set environment variables (optional — sensible defaults exist):

```bash
# Windows (PowerShell)
$env:SECRET_KEY="your-secret-key"
$env:DATABASE_URL="sqlite:///app.db"
$env:FLASK_APP="app"

# macOS / Linux
export SECRET_KEY="your-secret-key"
export DATABASE_URL="sqlite:///app.db"
export FLASK_APP="app"
```

**Populating the Database:**
To quickly get started with dummy accounts, sample visualisations, and default wellbeing resources, you can populate the database using the `setup()` function provided in `setup.py`. 

Run the following commands in your terminal to execute the setup script within the Flask application context:

```bash
flask shell
>>> from setup import setup
>>> setup()
>>> exit()
```

### Running the app

```bash
flask run
```

Then open <http://127.0.0.1:5000> in your browser.

## Usage

### Student Usage

1. Visit `/registration` and create an account with your University of Birmingham email (`@student.bham.ac.uk`). 
3. Submit your daily check-in at `/wellbeing` — rate each of stress, sleep, social, academic, and activity from 1 to 5, add optional notes, and submit.
4. View your average score and resource recommendations on the confirmation page.
5. Visit `/tracking` to see your history charted over time; use the dropdown to switch metrics.

### Admin Usage

Accounts registered with staff emails (`@bham.ac.uk`) are automatically granted administrative privileges. 

1. **Log in**: Admin users are redirected directly to the admin dashboard upon logging in.
2. **Resource Management (CRUD)**: Admins have exclusive access to `/admin/resources` to manage the wellbeing resources recommended to students.
   - **Create**: Add new helpful links by submitting a resource title, selecting a relevant category (Stress, Sleep, Social, Academic, Activity), and pasting the target URL.
   - **Read**: View the comprehensive list of all active resources currently presented to students.
   - **Update**: Click "Edit" on any existing resource to fix broken links, update titles, or re-categorise the content.
   - **Delete**: Click "Delete" to instantly remove outdated or irrelevant resources from the system.

## Data model

- **User** — account details, hashed password, owns responses and notifications. Admins are flagged via boolean.
- **WellbeingResponse** — one check-in per student per day: stress, sleep, social, academic, activity, notes, date.
- **Notification** — in-app reminders, generated on a schedule.
- **Resource** — wellbeing resource library managed by administrators.

## Validation rules

- Email must end in `@student.bham.ac.uk` or `@bham.ac.uk`.
- Password must be at least 8 characters and contain at least one digit.
- All five wellbeing metrics must be integers between 1 and 5.
- Users must consent to data collection to register.
- A student can only submit one check-in per calendar day.

## License

This is a piece of university coursework.
