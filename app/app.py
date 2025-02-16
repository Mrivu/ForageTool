import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
import json
import commands
import random
import math
import rarity

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
                getAdminStatus = "SELECT isAdmin FROM users WHERE username = ?"
                isAdmin = db.query(getAdminStatus, [username])
                session["isAdmin"] = isAdmin[0][0]
                getID = db.query("SELECT userID FROM users where username = ?", [session["username"]])
                session["userID"] = getID[0][0]
                bonus = db.query("SELECT forageBonus FROM users where username = ?", [session["username"]])
                session["forageBonus"] = bonus[0][0]
                multiplier = db.query("SELECT forageMultiplier FROM users where username = ?", [session["username"]])
                session["forageMultiplier"] = multiplier[0][0]
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
        bonus = int(request.form["bonus"])
        multiplier = int(request.form["multiplier"])
        isAdmin = request.form.get("admin", "no")
        isAdmin = 0 if isAdmin == "no" else 1
        print(username, password1, password2)
        if username == "" or password1 == "":
            return render_template("register.html", message = "The password and the username can't be empty")
        if password1 != password2:
            return render_template("register.html", message = "The passwords don't match")
        password_hash = generate_password_hash(password1)

        try:
            sql = "INSERT INTO users (username, password_hash, isAdmin, forageBonus, forageMultiplier) VALUES (?, ?, ?, ?, ?)"
            db.execute(sql, [username, password_hash, isAdmin, bonus, multiplier])
        except sqlite3.IntegrityError:
            return render_template("register.html", message = f"The username {username} is aready taken")

        session["username"] = username
        session["isAdmin"] = isAdmin
        session["forageBonus"] = bonus
        session["forageMultiplier"] = multiplier
        getID = db.query("SELECT userID FROM users where username = ?", [session["username"]])
        session["userID"] = getID[0][0]
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

@app.route("/inventory", methods = ["GET", "POST"])
def inventory():
    if request.method == "GET":
        inventory = commands.get_inventory(session["userID"], session["keyword"], session["selected_filter"])
        return render_template("inventory.html", message = "", inventory=inventory, keyword=session["keyword"], selected_filter=session["selected_filter"])
    if request.method == "POST":
        selected_filter = request.form["filter"]
        keyword = request.form["keyword"]
        inventory = commands.get_inventory(session["userID"], keyword, selected_filter)
        session["keyword"] = keyword
        session["selected_filter"] = selected_filter
        return render_template("inventory.html", message = "", inventory=inventory, keyword=session["keyword"], selected_filter=session["selected_filter"])
    
@app.route("/forage", methods = ["GET", "POST"])
def forage():
    if request.method == "GET":
       areas = db.query("SELECT * FROM areas")
       regions = db.query("SELECT * FROM regions")
       return render_template("forage.html", message="", areas=areas, regions=regions)
    if request.method == "POST":
        extraBonus = int(request.form.get("extraBonus") or 0)
        availability = int(request.form.get("plantAvailability") or 0)
        area = request.form["areas"]
        region = request.form["regions"]
        print(extraBonus, availability, area, region)
        diceroll = random.randint(1,20)+session["forageBonus"]+extraBonus
        print(diceroll)
        plantAmount = math.floor(diceroll / 10)+availability
        ## Check nat 20
        if (diceroll -  session["forageBonus"] - extraBonus) == 20:
            plantAmount += 1
        plantAmount = (plantAmount) * int(session["forageMultiplier"])
        print(plantAmount)
        if (diceroll > 40):
            diceroll = 40
        elif (diceroll < 1):
            diceroll = 1
        weights = [rarity.rollResults[diceroll-1]["Common"],
           rarity.rollResults[diceroll-1]["Uncommon"],
           rarity.rollResults[diceroll-1]["Rare"],
           rarity.rollResults[diceroll-1]["Very Rare"],
           rarity.rollResults[diceroll-1]["Legendary"]]
        if sum(weights) > 0:
            rarityResults = random.choices([1,2,3,4,5], weights=weights, k=plantAmount)
            for r in rarityResults:
                sql = "SELECT * FROM plants WHERE rarityID = ? ORDER BY RANDOM() LIMIT 1"
                plant_found = db.query(sql, [r])
                commands.add_to_inventory(plant_found[0], session["userID"])
        areas = db.query("SELECT * FROM areas")
        regions = db.query("SELECT * FROM regions")
        return render_template("forage.html", message=f"You rolled a {diceroll}", areas=areas, regions=regions)
        

@app.route("/import", methods = ["GET", "POST"])
def import_plants():
    if not session["isAdmin"]:
        abort(403)
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
                        commands.override_plant(plant, plant["name"])
                    elif not existingPlant:
                        commands.insert_plant(plant)
                return render_template("import.html", message = "JSON file read successfully!")
            except json.JSONDecodeError:
                return render_template("import.html", message = "Unable to read JSON file, invalid formatting")
    return render_template("import.html", message = "Invalid file type. Please upload a JSON file.")

@app.route("/profile", methods = ["GET", "POST"])
def profile():
    if request.method == "GET":
        user = db.query("SELECT * FROM users WHERE userID = ?", [session["userID"]])[0]
        return render_template("profile.html", message = "", user=user)
    if request.method == "POST":
        user = db.query("SELECT * FROM users WHERE userID = ?", [session["userID"]])[0]
        username = request.form["username"]
        bonus = int(request.form["bonus"])
        multiplier = int(request.form["multiplier"])
        isAdmin = request.form.get("admin", "no")
        isAdmin = 0 if isAdmin == "no" else 1
        if username == "":
            return render_template("profile.html", message = "The password and the username can't be empty", user=user)
        try:
            sql = """
                UPDATE users 
                SET username = ?, isAdmin = ?, forageBonus = ?, forageMultiplier = ?
                WHERE userID = ?
            """
            db.execute(sql, [username, isAdmin, bonus, multiplier, session["userID"]])
        except sqlite3.IntegrityError:
            return render_template("profile.html", message=f"The username {username} is already taken", user=user)

        session["username"] = username
        session["isAdmin"] = isAdmin
        session["forageBonus"] = bonus
        session["forageMultiplier"] = multiplier
        getID = db.query("SELECT userID FROM users where username = ?", [session["username"]])
        session["userID"] = getID[0][0]
        return redirect("/")

@app.route("/plants/<string:name>")
def view_plant(name):
    plant = commands.get_plant(name)
    source = request.args.get("source", "catalogue")
    return render_template("plant.html", plant=plant, source=source)

@app.route("/edit/<string:name>", methods = ["GET", "POST"])
def edit_plant(name):
    if not session["isAdmin"]:
        abort(403)
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
        commands.override_plant(plant, name)
        return redirect("/catalogue")

@app.route("/delete/<string:name>", methods = ["GET", "POST"])
def delete_plant(name):
    if not session["isAdmin"]:
        abort(403)
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