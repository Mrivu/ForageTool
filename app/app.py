import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
import db
import config
import json
import commands
import random
import math
import rarity
import users

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
        users.login(username, password)
        return render_template("main.html", message="Incorrect username or password")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", message="")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        bonus = int(request.form["bonus"])
        multiplier = int(request.form["multiplier"])
        isAdmin = request.form.get("admin", "no")
        print(password1, password2)
        
        result = users.register_user(username, password1, password2, bonus, multiplier, isAdmin)
        if result is not None:
            return result
        return redirect("/")
    
@app.route("/logout")
def logout():
    return users.logout()

@app.route("/catalogue", methods = ["GET", "POST"])
def catalogue():
    users.require_login()
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
    users.require_login()
    move_location = session.get("moveLocation")
    if move_location and move_location in commands.get_folders(session["userID"]):
        move_location = session["moveLocation"]
    if request.method == "GET":
        inventory = commands.get_inventory(session["userID"], session["keyword"], session["selected_filter"])
        folders = commands.get_folders(session["userID"])
        return render_template("inventory.html", move_location=move_location, message = "", inventory=inventory, keyword=session["keyword"], selected_filter=session["selected_filter"], folders=folders)
    if request.method == "POST":
        folders = commands.get_folders(session["userID"])
        selected_filter = request.form["filter"]
        keyword = request.form["keyword"]
        inventory = commands.get_inventory(session["userID"], keyword, selected_filter)
        session["keyword"] = keyword
        session["selected_filter"] = selected_filter
        return render_template("inventory.html", move_location=move_location, message = "", inventory=inventory, keyword=session["keyword"], selected_filter=session["selected_filter"], folders=folders)
    
@app.route("/newFolder", methods = ["POST"])
def newFolder():
    users.require_login()
    if request.method == "POST":
        folderName = request.form["newFolder"]
        print(session["userID"])
        commands.new_folder(session["userID"], folderName)
    return redirect("/inventory")

@app.route("/movePlant/<string:name>", methods = ["POST"])
def move_plant(name):
    users.require_login()
    if request.method == "POST":
        folderName = request.form["folder"]
        session["moveLocation"] = folderName
        commands.move_plant_to_folder(session["userID"], folderName, name)
    return redirect("/inventory")

@app.route("/unfolder/<string:folder>/<string:name>", methods = ["POST"])
def unfolder(folder, name):
    users.require_login()
    if request.method == "POST":
        folderName = folder
        commands.unfolder(session["userID"], folderName, name)
    return redirect("/inventory/"+folderName)

@app.route("/inventory/<string:name>", methods = ["GET", "POST"])
def display_folder(name):
    users.require_login()
    if request.method == "GET":
        folder = commands.get_folder_plants(session["userID"], name)
        return render_template("folder.html", message = "", name=name, folder=folder, keyword=session["keyword"], selected_filter=session["selected_filter"])
    if request.method == "POST":
        folder = commands.get_folder_plants(session["userID"], name)
        selected_filter = request.form["filter"]
        keyword = request.form["keyword"]
        session["keyword"] = keyword
        session["selected_filter"] = selected_filter
        return render_template("folder.html", message = "", name=name, folder=folder, keyword=session["keyword"], selected_filter=session["selected_filter"])

@app.route("/forage", methods = ["GET", "POST"])
def forage():
    users.require_login()
    if request.method == "GET":
       areas = db.query("SELECT * FROM areas")
       regions = db.query("SELECT * FROM regions")
       return render_template("forage.html", message="", areas=areas, regions=regions)
    if request.method == "POST":
        extraBonus = int(request.form.get("extraBonus") or 0)
        availability = int(request.form.get("plantAvailability") or 0)
        area = request.form["areas"]
        region = request.form["regions"]
        diceroll = random.randint(1,20)
        total = diceroll+session["forageBonus"]+extraBonus
        if (total > 40):
            total = 40
        elif (total < 1):
            total = 1
        plantAmount = math.floor(total / 10)+availability
        if diceroll == 20: ## Check nat 20
            plantAmount += 1
        plantAmount = (plantAmount) * int(session["forageMultiplier"])
        weights = [rarity.rollResults[total-1]["Common"],
           rarity.rollResults[total-1]["Uncommon"],
           rarity.rollResults[total-1]["Rare"],
           rarity.rollResults[total-1]["Very Rare"],
           rarity.rollResults[total-1]["Legendary"]]
        if sum(weights) > 0:
            rarityResults = random.choices([1,2,3,4,5], weights=weights, k=plantAmount)
            for r in rarityResults:
                sql = "SELECT * FROM plants WHERE rarityID = ? ORDER BY RANDOM() LIMIT 1"
                plant_found = db.query(sql, [r])
                commands.add_to_inventory(plant_found[0], session["userID"])
        areas = db.query("SELECT * FROM areas WHERE areaName = ?", [area])
        regions = db.query("SELECT * FROM regions WHERE regionName = ?", [region])
        
        # Statistics
        db.execute("UPDATE statistics SET timesForaged = timesForaged + 1 WHERE userID = ?", [session["userID"]])
        plants = commands.get_inventory(session["userID"], "", "Rarity")
        if plants:
            db.execute("UPDATE statistics SET highestRarity = ? WHERE userID = ?", [plants[-1]["rarity"], session["userID"]])

        return render_template("forage.html", message=f"You rolled a {total}", areas=areas, regions=regions)
        

@app.route("/import", methods = ["GET", "POST"])
def import_plants():
    users.require_login()
    users.require_admin()
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
    users.require_login()
    if request.method == "GET":
        statistics = db.query("SELECT * FROM statistics WHERE userID = ?", [session["userID"]])[0]
        user = db.query("SELECT * FROM users WHERE userID = ?", [session["userID"]])[0]
        return render_template("profile.html", message = "", user=user, statistics=statistics)
    if request.method == "POST":
        statistics = db.query("SELECT * FROM statistics WHERE userID = ?", [session["userID"]])[0]
        user = db.query("SELECT * FROM users WHERE userID = ?", [session["userID"]])[0]
        username = request.form["username"]
        bonus = int(request.form["bonus"])
        multiplier = int(request.form["multiplier"])
        isAdmin = request.form.get("admin", "no")
        isAdmin = 0 if isAdmin == "no" else 1
        if username == "":
            return render_template("profile.html", message = "The password and the username can't be empty", user=user, statistics=statistics)
        try:
            sql = """
                UPDATE users 
                SET username = ?, isAdmin = ?, forageBonus = ?, forageMultiplier = ?
                WHERE userID = ?
            """
            db.execute(sql, [username, isAdmin, bonus, multiplier, session["userID"]])
        except sqlite3.IntegrityError:
            return render_template("profile.html", message=f"The username {username} is already taken", user=user, statistics=statistics)

        session["username"] = username
        session["isAdmin"] = isAdmin
        session["forageBonus"] = bonus
        session["forageMultiplier"] = multiplier
        getID = db.query("SELECT userID FROM users where username = ?", [session["username"]])
        session["userID"] = getID[0][0]
        return redirect("/")

@app.route("/plants/<string:name>")
def view_plant(name):
    users.require_login()
    plant = commands.get_plant(name)
    source = request.args.get("source", "catalogue")
    return render_template("plant.html", plant=plant, source=source)

@app.route("/edit/<string:name>", methods = ["GET", "POST"])
def edit_plant(name):
    users.require_login()
    users.require_admin()
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
    users.require_login()
    users.require_admin()
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
        
@app.route("/deleteFolder/<string:name>", methods = ["POST"])
def delete_folder(name):
    users.require_login()
    if request.method == "POST":
        commands.delete_folder(session["userID"], name)
        return redirect("/inventory")
    
@app.route("/renameFolder/<string:name>", methods = ["POST"])
def rename_folder(name):
    users.require_login()
    if request.method == "POST":
        newName = request.form["newName"]
        commands.rename_folder(session["userID"], name, newName)
        return redirect("/inventory")