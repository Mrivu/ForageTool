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
import news

app = Flask(__name__)
app.secret_key = config.secret_key

@app.before_request
def refresh_user_data():
    if "userID" in session:
        user_data = db.query("SELECT isAdmin FROM users WHERE userID = ?", [session["userID"]])
        if user_data:
            session["isAdmin"] = user_data[0]['isAdmin']

@app.route("/", methods = ["GET", "POST"])
def user():
    if request.method == "GET":
        session["keyword"] = ""
        session["selected_filter"] = "Name"
        return render_template("main.html", message="", news=news.news)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users.login(username, password)
        return render_template("main.html", message="Incorrect username or password", news=news.news)

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

@app.route("/catalogue/<int:page_num>", methods=["GET", "POST"])
def catalogue(page_num=1):
    users.require_login(request)
    if request.method == "POST":
        session["keyword"] = request.form.get("keyword", "")
        session["selected_filter"] = request.form.get("filter", "Name")

    keyword = session.get("keyword", "")
    selected_filter = session.get("selected_filter", "Name")

    plants = commands.get_plants_by(keyword, selected_filter)
    page_count = max(math.ceil(len(plants) / 10), 1)
    plants = commands.get_plants_by(keyword, selected_filter, page_num)

    if page_num < 1:
        return redirect("/catalogue/1")
    if page_num > page_count:
        return redirect("/catalogue/" + str(page_count))
    
    return render_template("catalogue.html", message="", page=page_num, page_count=page_count, plants=plants, keyword=keyword, selected_filter=selected_filter)

@app.route("/inventory/<int:page_num>", methods = ["GET", "POST"])
def inventory(page_num=1):
    users.require_login(request)
    folders = commands.get_folders(session["userID"])
    move_location = session.get("moveLocation")
    if move_location and move_location in commands.get_folders(session["userID"]):
        move_location = session["moveLocation"]
    if request.method == "POST":
        selected_filter = request.form["filter"]
        keyword = request.form["keyword"]
        session["keyword"] = keyword
        session["selected_filter"] = selected_filter
    inventory = commands.get_inventory(session["userID"], session["keyword"], session["selected_filter"])
    page_count = max(math.ceil(len(inventory) / 10), 1)
    inventory = commands.get_inventory(session["userID"], session["keyword"], session["selected_filter"], page_num)
    if page_num < 1:
        return redirect("/inventoy/1")
    if page_num > page_count:
        return redirect("/inventory/" + str(page_count))
    return render_template("inventory.html", page=page_num, page_count=page_count, move_location=move_location, message = "", inventory=inventory, keyword=session["keyword"], selected_filter=session["selected_filter"], folders=folders)
    
@app.route("/newFolder", methods = ["POST"])
def newFolder():
    users.require_login(request)
    if request.method == "POST":
        folderName = request.form["newFolder"]
        print(session["userID"])
        commands.new_folder(session["userID"], folderName)
    return redirect("/inventory/1")

@app.route("/movePlant/<string:name>", methods = ["POST"])
def move_plant(name):
    users.require_login(request)
    if request.method == "POST":
        folderName = request.form["folder"]
        session["moveLocation"] = folderName
        commands.move_plant_to_folder(session["userID"], folderName, name)
    return redirect("/inventory/1")

@app.route("/removeFromInventory/<string:name>", methods = ["POST"])
def remove_from_inventory(name):
    users.require_login(request)
    if request.method == "POST":
        commands.remove_from_inventory(session["userID"], name)
    return redirect("/inventory/1")

@app.route("/unfolder/<string:folder>/<string:name>", methods = ["POST"])
def unfolder(folder, name):
    users.require_login(request)
    if request.method == "POST":
        folderName = folder
        commands.unfolder(session["userID"], folderName, name)
    return redirect("/inventory/"+folderName+"/1")

@app.route("/inventory/<string:name>/<int:page_num>", methods = ["GET", "POST"])
def display_folder(name, page_num=1):
    users.require_login(request)
    if request.method == "POST":
        selected_filter = request.form["filter"]
        keyword = request.form["keyword"]
        session["keyword"] = keyword
        session["selected_filter"] = selected_filter
    folder = commands.get_folder_plants(session["userID"], name, session["keyword"], session["selected_filter"])
    page_count = max(math.ceil(len(folder) / 10), 1)
    folder = commands.get_folder_plants(session["userID"], name, session["keyword"], session["selected_filter"], page_num)
    if page_num < 1:
        return redirect("/inventoy/" + name)
    if page_num > page_count:
        return redirect("/inventory/" + name + "/" + str(page_count))
    return render_template("folder.html", message = "", page=page_num, page_count=page_count, name=name, folder=folder, keyword=session["keyword"], selected_filter=session["selected_filter"])

@app.route("/forage", methods = ["GET", "POST"])
def forage():
    users.require_login(request)
    areas = db.query("SELECT areaName FROM areas")
    regions = db.query("SELECT regionName FROM regions")
    if request.method == "GET":
        return render_template("forage.html", message="", areas=areas, regions=regions)
    if request.method == "POST":
        try:
            file = request.files["plants"]
        except:
            file = None
        if file:
            if file and file.filename.endswith(".json"):
                try:
                    data = json.load(file)
                    for plant in data:
                        commands.add_to_inventory(plant, session["userID"], plant["count"])
                    return render_template("forage.html", areas=areas, regions=regions, message = "Plants added to inventory")
                except json.JSONDecodeError:
                    return render_template("forage.html", areas=areas, regions=regions, message = "Unable to read JSON file, invalid formatting")
            return render_template("forage.html", areas=areas, regions=regions, message = "Invalid file type. Please upload a JSON file.")
        if not commands.get_plants_by():
            return render_template("forage.html", message="No plants imported", areas=areas, regions=regions)
        extraBonus = int(request.form.get("extraBonus") or 0)
        availability = int(request.form.get("plantAvailability") or 0)
        area = request.form["areas"]
        region = request.form["regions"]
        manualDice = int(request.form["diceroll"])
        diceroll = manualDice if manualDice != 0 else random.randint(1,20)
        total = diceroll+session["forageBonus"]+extraBonus
        if (total > 40):
            total = 40
        elif (total < 1):
            total = 1
        print(total)
        plantAmount = math.floor(total / 10)+availability
        if diceroll == 20: ## Check nat 20
            plantAmount += 1
        print(plantAmount)
        plantAmount = (plantAmount) * int(session["forageMultiplier"])
        print(plantAmount)
        weights = [rarity.rollResults[total-1]["Common"],
           rarity.rollResults[total-1]["Uncommon"],
           rarity.rollResults[total-1]["Rare"],
           rarity.rollResults[total-1]["Very Rare"],
           rarity.rollResults[total-1]["Legendary"]]
        plants_found = []
        if sum(weights) > 0:
            rarityResults = random.choices([1,2,3,4,5], weights=weights, k=plantAmount)
            print(rarityResults)
            for r in rarityResults:
                plant_found = commands.forage_plant(r, area, region)
                commands.add_to_inventory(plant_found[0], session["userID"])
                plants_found.append(plant_found[0])
        
        # Statistics
        db.execute("UPDATE statistics SET timesForaged = timesForaged + 1 WHERE userID = ?", [session["userID"]])
        plants = commands.get_inventory(session["userID"], "", "Rarity")
        if plants:
            db.execute("UPDATE statistics SET highestRarity = ? WHERE userID = ?", [plants[-1]["rarity"], session["userID"]])

        return render_template("forage.html", message=f"You rolled a {total}!", plants_found=plants_found, areas=areas, regions=regions)
        

@app.route("/import", methods = ["GET", "POST"])
def import_plants():
    users.require_login(request)
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
    users.require_login(request)
    statistics = db.query("SELECT timesForaged, highestRarity FROM statistics WHERE userID = ?", [session["userID"]])[0]
    user = db.query("SELECT username, isAdmin, forageBonus, forageMultiplier FROM users WHERE userID = ?", [session["userID"]])[0]
    if request.method == "GET":
        return render_template("profile.html", message = "", user=user, statistics=statistics)
    if request.method == "POST":
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
    users.require_login(request)
    plant = commands.get_plant(name)
    source = request.args.get("source", "catalogue")
    page = request.args.get("page", 1)
    return render_template("plant.html", page=page, plant=plant, source=source)

@app.route("/edit/<string:name>", methods = ["GET", "POST"])
def edit_plant(name):
    users.require_login(request)
    users.require_admin()
    if request.method == "GET":
        plant = commands.get_plant(name)
        rarity = commands.get_rarity()
        return render_template("edit.html", rarity=rarity, plant=plant, message="")
    if request.method == "POST":
        plant = {}
        plant["name"] = request.form.get("Name")
        plant["rarity"] = request.form.get("Rarity")
        plant["Area"] = request.form.get("Area").split(",")
        plant["Region"] = request.form.get("Region").split(",")
        plant["Effects"] = request.form.get("Effects").split(",")
        plant["Description"] = request.form.get("Description")
        commands.override_plant(plant, name)
        return redirect(f"/catalogue/1")

@app.route("/delete/<string:name>", methods = ["GET", "POST"])
def delete_plant(name):
    users.require_login(request)
    users.require_admin()
    if request.method == "GET":
        plant = commands.get_plant(name)
        return render_template("delete.html", plant=plant)
    if request.method == "POST":
        action = request.form.get("button")
        if action == "yes":
            commands.delete_plant(name)
            return redirect(f"/catalogue/1")
        elif action == "no":
            return redirect(f"/catalogue/1")
        
@app.route("/deleteFolder/<string:name>", methods = ["POST"])
def delete_folder(name):
    users.require_login(request)
    if request.method == "POST":
        commands.delete_folder(session["userID"], name)
        return redirect("/inventory/1")
    
@app.route("/renameFolder/<string:name>", methods = ["POST"])
def rename_folder(name):
    users.require_login(request)
    if request.method == "POST":
        newName = request.form["newName"]
        commands.rename_folder(session["userID"], name, newName)
        return redirect("/inventory/1")