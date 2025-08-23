from flask import Flask, render_template, request, redirect, url_for, session, flash
from markupsafe import escape
from datetime import datetime
import os
from dotenv import load_dotenv
import pytz
from supabase import create_client, Client

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", os.urandom(24))

# ------------------------
# Supabase configuration
# ------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://vutgmbavjzqfwqxbnpci.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1dGdtYmF2anpxZndxeGJucGNpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ3MzY4NDgsImV4cCI6MjA3MDMxMjg0OH0.idxO7hT9weyYydbQ3Z8iW2sCVAcwn36BBLw7CLSNvRY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Inject Supabase config into templates
@app.context_processor
def inject_supabase():
    return dict(SUPABASE_URL=SUPABASE_URL, SUPABASE_KEY=SUPABASE_KEY)

# ------------------------
# Timezones
# ------------------------
TZ_MANILA = pytz.timezone("Asia/Manila")
TZ_MONROVIA = pytz.timezone("America/Los_Angeles")  # PST/PDT

# ------------------------
# Anniversary date
# ------------------------
ANNIV_YEAR = int(os.getenv("ANNIV_YEAR", "2024"))
ANNIV_MONTH = int(os.getenv("ANNIV_MONTH", "11"))
ANNIV_DAY = int(os.getenv("ANNIV_DAY", "18"))

def months_and_days_since(anniv_dt):
    today = datetime.now()
    total_days = (today - anniv_dt).days
    months = total_days // 30
    days = total_days % 30
    return months, days

# ------------------------
# Routes
# ------------------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = escape(request.form.get("username", "").strip())
        password = escape(request.form.get("password", "").strip())

        user = supabase.table("users").select("*")\
            .eq("username", username)\
            .eq("password", password).execute()

        if user.data:
            u = user.data[0]
            session["logged_in"] = True
            session["user_id"] = u["id"]
            session["username"] = u["username"]
            session["last_login"] = datetime.utcnow().isoformat()
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "error")
            return render_template("login.html")
    return render_template("login.html")


@app.route("/home")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    now_manila = datetime.now(TZ_MANILA).strftime("%I:%M:%S %p")
    now_monrovia = datetime.now(TZ_MONROVIA).strftime("%I:%M:%S %p")

    anniv_dt = datetime(ANNIV_YEAR, ANNIV_MONTH, ANNIV_DAY)
    months, days = months_and_days_since(anniv_dt)

    this_year_anniv = datetime(datetime.now().year, ANNIV_MONTH, ANNIV_DAY)
    if this_year_anniv < datetime.now():
        next_anniv = datetime(datetime.now().year + 1, ANNIV_MONTH, ANNIV_DAY)
    else:
        next_anniv = this_year_anniv
    days_until = (next_anniv - datetime.now()).days

    return render_template(
        "index.html",
        username=session.get("username"),
        manila_time=now_manila,
        monrovia_time=now_monrovia,
        months=months,
        days=days,
        days_until=days_until
    )

@app.route("/love-notes", methods=["GET", "POST"])
def love_notes():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":
        content = escape(request.form.get("content", "").strip())
        if content:
            supabase.table("love_notes").insert({
                "user_id": session["user_id"],
                "content": content
            }).execute()
            if request.is_json:
                return {"status": "ok"}
            flash("Note added!", "success")
            return redirect(url_for("love_notes"))

    notes = supabase.table("love_notes").select("*").order("created_at", desc=True).execute()
    return render_template("love_notes.html", notes=notes.data)

# ------------------------
# Mood board route
# ------------------------
@app.route("/mood", methods=["GET", "POST"])
def mood():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_id = session["user_id"]
    partner_id = session.get("partner_id")  # make sure this is set in session

    if request.method == "POST":
        mood_val = request.form.get("mood")
        if mood_val:
            # Use upsert to replace existing mood
            supabase.table("moods").upsert(
                {"user_id": user_id, "mood": mood_val},
                on_conflict=["user_id"]
            ).execute()
        return {"status": "ok"}

    # GET: return latest moods for both user & partner
    moods = supabase.table("moods").select("user_id, mood")\
        .in_("user_id", [user_id, partner_id])\
        .execute()
    return {"moods": moods.data}

@app.route("/memories", methods=["GET", "POST"])
def memories():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":
        title = escape(request.form.get("title", "").strip())
        image_url = escape(request.form.get("image_url", "").strip())
        description = escape(request.form.get("description", "").strip())
        supabase.table("memories").insert({
            "user_id": session["user_id"],
            "title": title,
            "image_url": image_url,
            "description": description
        }).execute()
        flash("Memory added!", "success")

    memories = supabase.table("memories").select("*").order("created_at", desc=True).execute()
    return render_template("memories.html", memories=memories.data)

@app.route("/special-days")
def special_days():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("special_days.html")

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    if request.method == "POST":
        flash("Settings saved (local only).", "info")
    return render_template("settings.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

# ------------------------
# Main
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
