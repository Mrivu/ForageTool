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
        return render_template("catalogue.html", message = "", plants=Plants, keyword=keyword, selected_filter=session["selected_filter"])

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
                    plantInsert = "INSERT INTO plants (name, rarity, Area, Region, Effects, description) VALUES (?, ?, ?, ?, ?, ?)"
                    Areas = "" 
                    Regions = "" 
                    Effects = ""
                    for i in plant["Area"]:
                        Areas += i + ", "
                    for i in plant["Region"]:
                        Regions += i + ", "
                    for i in plant["Effects"]:
                        Effects += i + ", "
                    Areas, Regions, Effects = Areas[:-2], Regions[:-2], Effects[:-2]
                    existingPlant = commands.get_plant(plant["name"])
                    if existingPlant and overwrite == "yes":
                        plantUpdate = """
                        UPDATE plants
                        SET Rarity = ?, Area = ?, Region = ?, Effects = ?, Description = ?
                        WHERE Name = ?
                        """
                        db.execute(plantUpdate, [plant["rarity"], Areas, Regions, Effects, plant["Description"], plant["name"]])
                    elif not existingPlant:
                        db.execute(plantInsert, (plant["name"], plant["rarity"], Areas, Regions, Effects, plant["Description"]))
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
        plant = commands.get_plant(name)
        
        Name = request.form.get("Name")
        Rarity = request.form.get("Rarity")
        Area = request.form.get("Area")
        Region = request.form.get("Region")
        Effects = request.form.get("Effects")
        Description = request.form.get("Description")

        fields = [Name, Rarity, Area, Region, Effects, Description]
        for field in fields:
            if field == "":
                return render_template("edit.html", plant=plant, message="A field cannot be empty")
        sql = """
        UPDATE plants
        SET Name = ?, Rarity = ?, Area = ?, Region = ?, Effects = ?, Description = ?
        WHERE Name = ?
        """
        db.execute(sql, [fields[0], fields[1], fields[2], fields[3], fields[4], fields[5], plant["Name"]])
        return redirect("/catalogue")

@app.route("/delete/<string:name>", methods = ["GET", "POST"])
def delete_plant(name):
    if request.method == "GET":
        plant = commands.get_plant(name)
        return render_template("delete.html", plant=plant)
    if request.method == "POST":
        action = request.form.get("button")
        if action == "yes":
            db.execute("DELETE FROM plants WHERE name = ?", (name,))
            return redirect("/catalogue")
        elif action == "no":
            return redirect("/catalogue")