from flask import Flask, render_template, request, redirect, url_for, session, flash
from markupsafe import escape
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import pytz

# Load .env (optional)
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", os.urandom(24))

# Password (change in .env or env var)
APP_PASSWORD = os.getenv("SCRAPBOOK_PASSWORD", "loveisbeautiful")

# Timezones
TZ_MANILA = pytz.timezone("Asia/Manila")
TZ_MONROVIA = pytz.timezone("America/Los_Angeles")  # Monrovia CA (PST/PDT)

# Anniversary date (change to your actual anniversary)
ANNIV_YEAR = int(os.getenv("ANNIV_YEAR", "2023"))
ANNIV_MONTH = int(os.getenv("ANNIV_MONTH", "5"))
ANNIV_DAY = int(os.getenv("ANNIV_DAY", "20"))

def months_and_days_since(anniv_dt):
    today = datetime.now()
    total_days = (today - anniv_dt).days
    months = total_days // 30
    days = total_days % 30
    return months, days

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pwd = escape(request.form.get("password", "").strip())
        if pwd == APP_PASSWORD:
            session["logged_in"] = True
            session["last_login"] = datetime.utcnow().isoformat()
            return redirect(url_for("index"))
        else:
            flash("Invalid password. Try again.", "error")
            return render_template("login.html")
    return render_template("login.html")

def require_login():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return None

@app.route("/home")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    now_manila = datetime.now(TZ_MANILA).strftime("%I:%M:%S %p")
    now_monrovia = datetime.now(TZ_MONROVIA).strftime("%I:%M:%S %p")

    anniv_dt = datetime(ANNIV_YEAR, ANNIV_MONTH, ANNIV_DAY)
    months, days = months_and_days_since(anniv_dt)

    # days until next anniversary
    this_year_anniv = datetime(datetime.now().year, ANNIV_MONTH, ANNIV_DAY)
    if this_year_anniv < datetime.now():
        next_anniv = datetime(datetime.now().year + 1, ANNIV_MONTH, ANNIV_DAY)
    else:
        next_anniv = this_year_anniv
    days_until = (next_anniv - datetime.now()).days

    return render_template(
        "index.html",
        manila_time=now_manila,
        monrovia_time=now_monrovia,
        months=months,
        days=days,
        days_until=days_until
    )

@app.route("/love-notes")
def love_notes():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("love_notes.html")

@app.route("/memories")
def memories():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("memories.html")

@app.route("/special-days")
def special_days():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("special_days.html")

@app.route("/settings", methods=["GET","POST"])
def settings():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    if request.method == "POST":
        # update simple settings locally (placeholder)
        flash("Settings saved (local only).", "info")
    return render_template("settings.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
