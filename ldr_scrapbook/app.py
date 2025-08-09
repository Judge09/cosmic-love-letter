from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import pytz
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")  # Change this in production

# Dummy credentials (replace with Supabase auth later)
USERNAME = "love"
PASSWORD = "you"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/home")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    # Timezones
    monrovia_time = datetime.now(pytz.timezone("America/Los_Angeles")).strftime("%I:%M:%S %p")
    manila_time = datetime.now(pytz.timezone("Asia/Manila")).strftime("%I:%M:%S %p")
    return render_template("index.html", monrovia_time=monrovia_time, manila_time=manila_time)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
