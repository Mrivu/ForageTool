import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def user():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", message="")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql_password = "SELECT password_hash FROM users WHERE username = ?"
        password_hash = db.query(sql_password, [username])

        if password_hash:
            password_hash = password_hash[0][0]
            if check_password_hash(password_hash, password):
                session["username"] = username
                return redirect("/")
        return render_template("login.html", message="VIRHE: väärä tunnus tai salasana")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", message = "")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return render_template("register.html", message = "VIRHE: salasanat eivät ole samat")
        password_hash = generate_password_hash(password1)

        try:
            sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
            db.execute(sql, [username, password_hash])
        except sqlite3.IntegrityError:
            return render_template("register.html", message = "VIRHE: tunnus on jo varattu")

        session["username"] = username
        return redirect("/")
    
@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")