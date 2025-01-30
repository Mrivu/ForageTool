import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
import json
import os

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/", methods = ["GET", "PUSH"])
def user():
    if request.method == "GET":
        return render_template("main.html")
    if request.method == "POST":
        pass


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

@app.route("/catalogue")
def catalogue():
    return render_template("catalogue.html", message = "")

@app.route("/import", methods = ["GET", "POST"])
def importPlants():
    if request.method == "GET":
        return render_template("import.html")
    if request.method == "POST":
        file = request.files["plants"]
        if file and file.filename.endswith(".json"):
            try:
                data = json.load(file)
                return render_template("import.html", message = "JSON file read successfully!")
            except json.JSONDecodeError:
                return render_template("import.html", message = "Unable to read JSON file, invalid formatting")


    return render_template("import.html", message = "Invalid file type. Please upload a JSON file.")