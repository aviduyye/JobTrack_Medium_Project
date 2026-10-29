import csv
import io
import os
import sqlite3
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, Response, g

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
DATABASE = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "jobtrack.db"))

STATUSES = ["Wishlist", "Applied", "Assessment", "Interview", "Offer", "Rejected"]

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                location TEXT DEFAULT '',
                job_type TEXT DEFAULT 'Full-time',
                status TEXT NOT NULL DEFAULT 'Wishlist',
                applied_date TEXT DEFAULT '',
                salary TEXT DEFAULT '',
                job_link TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)
        g.db.commit()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def get_stats(db):
    total = db.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    applied = db.execute("SELECT COUNT(*) FROM applications WHERE status = 'Applied'").fetchone()[0]
    interviews = db.execute("SELECT COUNT(*) FROM applications WHERE status = 'Interview'").fetchone()[0]
    offers = db.execute("SELECT COUNT(*) FROM applications WHERE status = 'Offer'").fetchone()[0]
    return {"total": total, "applied": applied, "interviews": interviews, "offers": offers}

@app.route("/")
def dashboard():
    db = get_db()
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    query = "SELECT * FROM applications WHERE 1=1"
    params = []
    if search:
        query += " AND (company LIKE ? OR role LIKE ? OR location LIKE ?)"
        pattern = f"%{search}%"
        params.extend([pattern, pattern, pattern])
    if status in STATUSES:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY created_at DESC, id DESC"
    applications = db.execute(query, params).fetchall()
    stats = get_stats(db)
    status_rows = db.execute(
        "SELECT status, COUNT(*) AS count FROM applications GROUP BY status"
    ).fetchall()
    status_counts = {row["status"]: row["count"] for row in status_rows}
    return render_template(
        "dashboard.html", applications=applications, stats=stats,
        statuses=STATUSES, selected_status=status, search=search,
        status_counts=status_counts, today=date.today().isoformat()
    )

@app.route("/add", methods=["GET", "POST"])
def add_application():
    if request.method == "POST":
        company = request.form.get("company", "").strip()
        role = request.form.get("role", "").strip()
        if not company or not role:
            flash("Company name and job role are required.", "error")
            return render_template("form.html", application=request.form, statuses=STATUSES, page_title="Add Application")
        status = request.form.get("status", "Wishlist")
        if status not in STATUSES:
            status = "Wishlist"
        db = get_db()
        db.execute("""
            INSERT INTO applications
            (company, role, location, job_type, status, applied_date, salary, job_link, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            company, role, request.form.get("location", "").strip(),
            request.form.get("job_type", "Full-time"), status,
            request.form.get("applied_date", "").strip(),
            request.form.get("salary", "").strip(),
            request.form.get("job_link", "").strip(),
            request.form.get("notes", "").strip(), date.today().isoformat()
        ))
        db.commit()
        flash("Application added successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("form.html", application={}, statuses=STATUSES, page_title="Add Application")

@app.route("/edit/<int:application_id>", methods=["GET", "POST"])
def edit_application(application_id):
    db = get_db()
    application = db.execute("SELECT * FROM applications WHERE id = ?", (application_id,)).fetchone()
    if application is None:
        flash("Application not found.", "error")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        company = request.form.get("company", "").strip()
        role = request.form.get("role", "").strip()
        if not company or not role:
            flash("Company name and job role are required.", "error")
            return render_template("form.html", application=request.form, statuses=STATUSES, page_title="Edit Application", application_id=application_id)
        status = request.form.get("status", "Wishlist")
        if status not in STATUSES:
            status = "Wishlist"
        db.execute("""
            UPDATE applications SET company=?, role=?, location=?, job_type=?, status=?,
            applied_date=?, salary=?, job_link=?, notes=? WHERE id=?
        """, (
            company, role, request.form.get("location", "").strip(),
            request.form.get("job_type", "Full-time"), status,
            request.form.get("applied_date", "").strip(),
            request.form.get("salary", "").strip(),
            request.form.get("job_link", "").strip(),
            request.form.get("notes", "").strip(), application_id
        ))
        db.commit()
        flash("Application updated successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("form.html", application=application, statuses=STATUSES, page_title="Edit Application", application_id=application_id)

@app.route("/delete/<int:application_id>", methods=["POST"])
def delete_application(application_id):
    db = get_db()
    db.execute("DELETE FROM applications WHERE id = ?", (application_id,))
    db.commit()
    flash("Application deleted.", "success")
    return redirect(url_for("dashboard"))

@app.route("/export")
def export_csv():
    db = get_db()
    rows = db.execute("""
        SELECT company, role, location, job_type, status, applied_date, salary, job_link, notes
        FROM applications ORDER BY created_at DESC, id DESC
    """).fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Company", "Role", "Location", "Job Type", "Status", "Applied Date", "Salary", "Job Link", "Notes"])
    for row in rows:
        writer.writerow(list(row))
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=jobtrack_applications.csv"}
    )

@app.route("/health")
def health():
    return {"status": "ok", "app": "JobTrack"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
