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
app.config['APPLICATION_ROOT'] = config.app_route

@app.before_request
def refresh_user_data():
    if "userID" in session:
        user_data = db.query("SELECT isAdmin FROM users WHERE userID = ?", [session["userID"]])
        if user_data:
            session["isAdmin"] = user_data[0]['isAdmin']
        else:
            logout()

@app.route(config.app_route, methods = ["GET", "POST"])
def user():
    if request.method == "GET":
        session["keyword"] = ""
        session["selected_filter"] = "Name"
        return render_template("main.html", config=config, message="", news=news.news)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users.login(username, password)
        return render_template("main.html", config=config, message="Incorrect username or password", news=news.news)

@app.route(config.app_route + "/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", config=config, message="")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        bonus = int(request.form["bonus"])
        multiplier = int(request.form["multiplier"])
        
        result = users.register_user(username, password1, password2, bonus, multiplier)
        if result is not None:
            return result
        return redirect(config.app_route)
    
@app.route(config.app_route + "/logout")
def logout():
    return users.logout()

@app.route(config.app_route + "/catalogue/<int:page_num>", methods=["GET", "POST"])
def catalogue(page_num=1):
    users.require_login(request)
    if request.method == "POST":
        session["keyword"] = request.form.get("keyword", "")
        session["selected_filter"] = request.form.get("filter", "Name")

    keyword = session.get("keyword", "")
    selected_filter = session.get("selected_filter", "Name")

    plants = commands.get_plants_by(keyword, selected_filter)
    page_count = max(math.ceil(len(plants) / config.page_size), 1)
    plants = commands.get_plants_by(keyword, selected_filter, page_num)

    if page_num < 1:
        return redirect(config.app_route + "/catalogue/1")
    if page_num > page_count:
        return redirect(config.app_route + "/catalogue/" + str(page_count))

    found = commands.get_found(session["userID"])
    return render_template("catalogue.html", config=config, message="", found=found, page=page_num, page_count=page_count, plants=plants, keyword=keyword, selected_filter=selected_filter)

@app.route(config.app_route + "/inventory/<int:page_num>", methods = ["GET", "POST"])
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
    page_count = max(math.ceil(len(inventory) / config.page_size), 1)
    inventory = commands.get_inventory(session["userID"], session["keyword"], session["selected_filter"], page_num)
    if page_num < 1:
        return redirect(config.app_route + "/inventoy/1")
    if page_num > page_count:
        return redirect(config.app_route + "/inventory/" + str(page_count))
    return render_template("inventory.html", config=config, page=page_num, page_count=page_count, move_location=move_location, message = "", inventory=inventory, keyword=session["keyword"], selected_filter=session["selected_filter"], folders=folders)
    
@app.route(config.app_route + "/newFolder", methods = ["POST"])
def newFolder():
    users.require_login(request)
    if request.method == "POST":
        folderName = request.form["newFolder"]
        commands.new_folder(session["userID"], folderName)
    return redirect(config.app_route + "/inventory/1")

@app.route(config.app_route + "/movePlant/<string:name>", methods = ["POST"])
def move_plant(name):
    users.require_login(request)
    if request.method == "POST":
        folderName = request.form["folder"]
        session["moveLocation"] = folderName
        commands.move_plant_to_folder(session["userID"], folderName, name)
    return redirect(config.app_route + "/inventory/1")

@app.route(config.app_route + "/removeFromInventory/<string:name>", methods = ["POST"])
def remove_from_inventory(name):
    users.require_login(request)
    if request.method == "POST":
        commands.remove_from_inventory(session["userID"], name)
    return redirect(config.app_route + "/inventory/1")

@app.route(config.app_route + "/unfolder/<string:folder>/<string:name>", methods = ["POST"])
def unfolder(folder, name):
    users.require_login(request)
    if request.method == "POST":
        folderName = folder
        commands.unfolder(session["userID"], folderName, name)
    return redirect(config.app_route + "/inventory/"+folderName+"/1")

@app.route(config.app_route + "/inventory/<string:name>/<int:page_num>", methods = ["GET", "POST"])
def display_folder(name, page_num=1):
    users.require_login(request)
    if request.method == "POST":
        selected_filter = request.form["filter"]
        keyword = request.form["keyword"]
        session["keyword"] = keyword
        session["selected_filter"] = selected_filter
    folder = commands.get_folder_plants(session["userID"], name, session["keyword"], session["selected_filter"])
    page_count = max(math.ceil(len(folder) / config.page_size), 1)
    folder = commands.get_folder_plants(session["userID"], name, session["keyword"], session["selected_filter"], page_num)
    if page_num < 1:
        return redirect(config.app_route + "/inventoy/" + name)
    if page_num > page_count:
        return redirect(config.app_route + "/inventory/" + name + "/" + str(page_count))
    return render_template("folder.html", config=config, message = "", page=page_num, page_count=page_count, name=name, folder=folder, keyword=session["keyword"], selected_filter=session["selected_filter"])

@app.route(config.app_route + "/forage", methods = ["GET", "POST"])
def forage():
    users.require_login(request)
    areas = db.query("SELECT areaName FROM areas")
    regions = db.query("SELECT regionName FROM regions")
    if request.method == "GET":
        return render_template("forage.html", config=config, message="", areas=areas, regions=regions)
    if request.method == "POST":
        session["areaFilter"] = request.form.get("areas", None)
        session["regionFilter"] = request.form.get("regions", None)
        try:
            file = request.files["plants"]
        except:
            file = None
        if file:
            if file and file.filename.endswith(".json"):
                try:
                    data = json.load(file)
                    for plant in data:
                        if "count" not in plant or "plantName" not in plant:
                            return render_template("forage.html", config=config, areas=areas, regions=regions, message = "Invalid manual import file. See the github for help.")
                        if not commands.get_plant(plant["plantName"]):
                            return render_template("forage.html", config=config, areas=areas, regions=regions, message = "Invalid plant in import. See the github for help.")
                        commands.add_to_inventory(plant, session["userID"], plant["count"])
                    return render_template("forage.html", config=config, areas=areas, regions=regions, message = "Plants added to inventory")
                except json.JSONDecodeError:
                    return render_template("forage.html", config=config, areas=areas, regions=regions, message = "Unable to read JSON file, invalid formatting")
            return render_template("forage.html", config=config, areas=areas, regions=regions, message = "Invalid file type. Please upload a JSON file.")
        if not commands.get_plants_by():
            return render_template("forage.html", config=config, message="No plants imported", areas=areas, regions=regions)
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
        plantAmount = math.floor(total / 10)+availability
        if diceroll == 20: ## Check nat 20
            plantAmount += 1
        plantAmount = (plantAmount) * int(session["forageMultiplier"])
        weights = [rarity.rollResults[total-1]["Common"],
           rarity.rollResults[total-1]["Uncommon"],
           rarity.rollResults[total-1]["Rare"],
           rarity.rollResults[total-1]["Very Rare"],
           rarity.rollResults[total-1]["Legendary"]]
        plants_found = []
        if sum(weights) > 0:
            rarityResults = random.choices([1,2,3,4,5], weights=weights, k=plantAmount)
            for r in rarityResults:
                plant_found = commands.forage_plant(r, area, region)
                if plant_found:
                    commands.add_to_inventory(plant_found[0], session["userID"])
                    plants_found.append(plant_found[0])
        
        # Statistics
        db.execute("UPDATE statistics SET timesForaged = timesForaged + 1 WHERE userID = ?", [session["userID"]])
        plants = commands.get_inventory(session["userID"], "", "Rarity")
        if plants:
            db.execute("UPDATE statistics SET highestRarity = ? WHERE userID = ?", [plants[-1]["rarity"], session["userID"]])

        return render_template("forage.html", config=config, message=f"You rolled a {total}!", plants_found=plants_found, areas=areas, regions=regions)
        

@app.route(config.app_route + "/import", methods = ["GET", "POST"])
def import_plants():
    users.require_login(request)
    users.require_admin()
    if request.method == "GET":
        return render_template("import.html", config=config)
    if request.method == "POST":
        file = request.files["plants"]
        overwrite = request.form.get("overwrite", "no")
        if file and file.filename.endswith(".json"):
            try:
                data = json.load(file)
                for plant in data:
                    existingPlant = commands.is_plant(plant["name"])
                    if overwrite == "yes" and existingPlant:
                        commands.override_plant(plant, plant["name"])
                    elif not existingPlant:
                        commands.insert_plant(plant)
                return render_template("import.html", config=config, message = "JSON file read successfully!")
            except json.JSONDecodeError:
                return render_template("import.html", config=config, message = "Unable to read JSON file, invalid formatting")
    return render_template("import.html", config=config, message = "Invalid file type. Please upload a JSON file.")

@app.route(config.app_route + "/profile", methods = ["GET", "POST"])
def profile():
    users.require_login(request)
    statistics = db.query("SELECT timesForaged, highestRarity FROM statistics WHERE userID = ?", [session["userID"]])[0]
    user = db.query("SELECT username, forageBonus, forageMultiplier FROM users WHERE userID = ?", [session["userID"]])[0]
    if request.method == "GET":
        return render_template("profile.html", config=config, message = "", user=user, statistics=statistics)
    if request.method == "POST":
        username = request.form["username"]
        bonus = int(request.form["bonus"])
        multiplier = int(request.form["multiplier"])
        if username == "":
            return render_template("profile.html", config=config, message = "The password and the username can't be empty", user=user, statistics=statistics)
        try:
            sql = """
                UPDATE users 
                SET username = ?, forageBonus = ?, forageMultiplier = ?
                WHERE userID = ?
            """
            db.execute(sql, [username, bonus, multiplier, session["userID"]])
        except sqlite3.IntegrityError:
            return render_template("profile.html", config=config, message=f"The username {username} is already taken", user=user, statistics=statistics)

        session["username"] = username
        session["forageBonus"] = bonus
        session["forageMultiplier"] = multiplier
        getID = db.query("SELECT userID FROM users where username = ?", [session["username"]])
        session["userID"] = getID[0][0]
        return redirect(config.app_route)

@app.route(config.app_route + "/plants/<int:id>")
def view_plant(id):
    users.require_login(request)
    found = commands.get_found(session["userID"])
    plant = commands.get_plant(None, id)
    source = request.args.get("source", "catalogue")
    page = request.args.get("page", 1)
    return render_template("plant.html", config=config, page=page, plant=plant, source=source, found=found)

@app.route(config.app_route + "/edit/<string:name>", methods = ["GET", "POST"])
def edit_plant(name):
    users.require_login(request)
    users.require_admin()
    if request.method == "GET":
        plant = commands.get_plant(name)
        rarity = commands.get_rarity()
        return render_template("edit.html", config=config, rarity=rarity, plant=plant, message="")
    if request.method == "POST":
        plant = {}
        plant["name"] = request.form.get("Name")
        plant["rarity"] = request.form.get("Rarity")
        plant["Area"] = request.form.get("Area").split(",")
        plant["Region"] = request.form.get("Region").split(",")
        plant["Effects"] = request.form.get("Effects").split(",")
        plant["Description"] = request.form.get("Description")
        unobtainable = int(request.form.get("unobtainable", 0))
        isHidden = int(request.form.get("isHidden", 0))
        isSecret = int(request.form.get("isSecret", 0))
        commands.override_plant(plant, name, [unobtainable, isHidden, isSecret])
        return redirect(config.app_route + "/catalogue/1")

@app.route(config.app_route + "/delete/<string:name>", methods = ["GET", "POST"])
def delete_plant(name):
    users.require_login(request)
    users.require_admin()
    if request.method == "GET":
        plant = commands.get_plant(name)
        return render_template("delete.html", config=config, plant=plant)
    if request.method == "POST":
        action = request.form.get("button")
        if action == "yes":
            commands.delete_plant(name)
            return redirect(config.app_route + "/catalogue/1")
        elif action == "no":
            return redirect(config.app_route + "/catalogue/1")
        
@app.route(config.app_route + "/deleteFolder/<string:name>", methods = ["POST"])
def delete_folder(name):
    users.require_login(request)
    if request.method == "POST":
        commands.delete_folder(session["userID"], name)
        return redirect(config.app_route + "/inventory/1")
    
@app.route(config.app_route + "/renameFolder/<string:name>", methods = ["POST"])
def rename_folder(name):
    users.require_login(request)
    if request.method == "POST":
        newName = request.form["newName"]
        commands.rename_folder(session["userID"], name, newName)
        return redirect(config.app_route + "/inventory/1")