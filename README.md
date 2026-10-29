# JobTrack — Medium-Level Flask Project

JobTrack is a responsive job application tracker built with Python, Flask, SQLite, HTML, CSS, and JavaScript. It is designed as a medium-level portfolio/college project and can be deployed as a Render Web Service.

## Features

- Dashboard cards for total applications, applied jobs, interviews, and offers
- Add, edit, and delete job applications
- Search by company, role, or location
- Filter applications by status
- Application pipeline overview with progress bars
- Store location, job type, date, salary/stipend, posting link, and notes
- Export all records to CSV
- Responsive layout for desktop and mobile
- Confirmation before deleting records
- Health-check route at `/health`
- SQLite database created automatically

## Project structure

```text
JobTrack_Medium_Project/
├── app.py
├── requirements.txt
├── render.yaml
├── README.md
├── jobtrack.db          # created automatically when the app runs
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   └── form.html
└── static/
    ├── app.js
    └── style.css
```

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal inside this folder.
3. Install the packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Run:

   ```bash
   python app.py
   ```

5. Open `http://127.0.0.1:5000`.

## Deploy on Render

1. Upload all project files to a GitHub repository.
2. In Render, choose **New + → Web Service** and connect the repository.
3. Use these settings:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
4. Click **Create Web Service** and wait for deployment.
5. Open the public URL Render provides.

The included `render.yaml` can also be used as a Blueprint configuration.

## Important database note

This starter version uses SQLite, so it works without configuring an external database. On Render, the normal web-service filesystem is ephemeral: SQLite records can be lost after a redeploy or instance replacement. For durable production data, configure a persistent disk (where available) and set `DATABASE_PATH` to a path on that disk, or migrate the app to a managed PostgreSQL database.

## Routes

- `/` — Dashboard
- `/add` — Add an application
- `/edit/<id>` — Edit an application
- `/delete/<id>` — Delete an application (POST only)
- `/export` — Download CSV
- `/health` — Health-check JSON
