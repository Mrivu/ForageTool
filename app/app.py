import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
import json
import commands

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/", methods = ["GET", "POST"])
def user():
    if request.method == "GET":
        session["keyword"] = ""
        session["selected_filter"] = "Name"
        return render_template("main.html", message="")
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
        return render_template("main.html", message="Incorrect username or password")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", message = "")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        print(username, password1, password2)
        if username == "" or password1 == "":
            return render_template("register.html", message = "The password and the username can't be empty")
        if password1 != password2:
            return render_template("register.html", message = "The passwords don't match")
        password_hash = generate_password_hash(password1)

        try:
            sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
            db.execute(sql, [username, password_hash])
        except sqlite3.IntegrityError:
            return render_template("register.html", message = f"The username {username} is aready taken")

        session["username"] = username
        return redirect("/")
    
@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/catalogue", methods = ["GET", "POST"])
def catalogue():
    if request.method == "GET":
        Plants = commands.get_plants_by(session["keyword"], session["selected_filter"])
        return render_template("catalogue.html", message = "", plants=Plants, keyword=session["keyword"], selected_filter=session["selected_filter"])
    if request.method == "POST":
        selected_filter = request.form["filter"]
        keyword = request.form["keyword"]
        Plants = commands.get_plants_by(keyword, selected_filter)
        session["keyword"] = keyword
        session["selected_filter"] = selected_filter
        return render_template("catalogue.html", message = "", plants=Plants, keyword=session["keyword"], selected_filter=session["selected_filter"])

@app.route("/import", methods = ["GET", "POST"])
def import_plants():
    if request.method == "GET":
        return render_template("import.html")
    if request.method == "POST":
        file = request.files["plants"]
        overwrite = request.form.get("overwrite", "no")
        if file and file.filename.endswith(".json"):
            try:
                data = json.load(file)
                for plant in data:
                    existingPlant = commands.get_plant(plant["name"])
                    if existingPlant and overwrite == "yes":
                        commands.override_plant(plant)
                    elif not existingPlant:
                        commands.insert_plant(plant)
                return render_template("import.html", message = "JSON file read successfully!")
            except json.JSONDecodeError:
                return render_template("import.html", message = "Unable to read JSON file, invalid formatting")
    return render_template("import.html", message = "Invalid file type. Please upload a JSON file.")

@app.route("/plants/<string:name>")
def view_plant(name):
    plant = commands.get_plant(name)
    return render_template("plant.html", plant=plant)

@app.route("/edit/<string:name>", methods = ["GET", "POST"])
def edit_plant(name):
    if request.method == "GET":
        plant = commands.get_plant(name)
        return render_template("edit.html", plant=plant, message="")
    if request.method == "POST":
        plant = {}
        plant["name"] = request.form.get("Name")
        plant["rarity"] = request.form.get("Rarity")
        plant["Area"] = request.form.get("Area").split(",")
        plant["Region"] = request.form.get("Region").split(",")
        plant["Effects"] = request.form.get("Effects").split(",")
        plant["Description"] = request.form.get("Description")
        commands.delete_plant(name)
        commands.insert_plant(plant)
        return redirect("/catalogue")

@app.route("/delete/<string:name>", methods = ["GET", "POST"])
def delete_plant(name):
    if request.method == "GET":
        plant = commands.get_plant(name)
        return render_template("delete.html", plant=plant)
    if request.method == "POST":
        action = request.form.get("button")
        if action == "yes":
            commands.delete_plant(name)
            return redirect("/catalogue")
        elif action == "no":
            return redirect("/catalogue")