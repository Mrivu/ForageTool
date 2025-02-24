import db
import rarity
import sqlite3

filterReference = {
            "Name": "p.plantName",
            "Rarity": "p.rarityID",
            "Description": "p.plantDescription",
            "Area": "a.areaName",
            "Region": "r.regionName",
            "Effects": "e.effectName"
    }

def get_plant(name):
    sql = """
    SELECT 
        p.plantName,
        p.rarity,
        p.rarityID,
        p.plantDescription,
        GROUP_CONCAT(DISTINCT a.areaName) AS plantAreas,
        GROUP_CONCAT(DISTINCT r.regionName) AS plantRegions,
        (SELECT GROUP_CONCAT(effectName) 
        FROM effect 
        WHERE plantName = p.plantName) AS plantEffects
    FROM plants p
    JOIN area    pa ON p.plantName = pa.plantName
    JOIN areas   a  ON pa.areaName = a.areaName
    JOIN region  pr ON p.plantName = pr.plantName
    JOIN regions r  ON pr.regionName = r.regionName
    JOIN effect  pe ON p.plantName = pe.plantName
    JOIN effects e  ON pe.effectName = e.effectName
    WHERE p.plantName = ?
    GROUP BY p.plantName, p.rarity, p.plantDescription
    """
    plant = db.query(sql, [name])
    if plant:
        return plant[0]
    return None

def get_inventory(id, keyword, filter):
    sql = f"""
    SELECT 
        p.plantName,
        p.rarity,
        p.rarityID,
        p.plantDescription,
        GROUP_CONCAT(DISTINCT a.areaName) AS plantAreas,
        GROUP_CONCAT(DISTINCT r.regionName) AS plantRegions,
        GROUP_CONCAT(DISTINCT e.effectName) AS plantEffects,
        i.quantity
    FROM inventory i
    JOIN plants p ON i.plantName = p.plantName
    LEFT JOIN area pa ON p.plantName = pa.plantName
    LEFT JOIN areas a ON pa.areaName = a.areaName
    LEFT JOIN region pr ON p.plantName = pr.plantName
    LEFT JOIN regions r ON pr.regionName = r.regionName
    LEFT JOIN effect pe ON p.plantName = pe.plantName
    LEFT JOIN effects e ON pe.effectName = e.effectName
    WHERE i.userID = ?
    AND {filterReference[filter]} LIKE ?
    GROUP BY p.plantName, p.rarity, p.rarityID, p.plantDescription, i.quantity
    ORDER BY {filterReference[filter]}
    """

    result = db.query(sql, [id, "%" + keyword + "%"])
    if keyword == "":
        sql = f"""
        SELECT 
            p.plantName,
            p.rarity,
            p.rarityID,
            p.plantDescription,
            GROUP_CONCAT(DISTINCT a.areaName) AS plantAreas,
            GROUP_CONCAT(DISTINCT r.regionName) AS plantRegions,
            GROUP_CONCAT(DISTINCT e.effectName) AS plantEffects,
            i.quantity
        FROM inventory i
        JOIN plants p ON i.plantName = p.plantName
        LEFT JOIN area pa ON p.plantName = pa.plantName
        LEFT JOIN areas a ON pa.areaName = a.areaName
        LEFT JOIN region pr ON p.plantName = pr.plantName
        LEFT JOIN regions r ON pr.regionName = r.regionName
        LEFT JOIN effect pe ON p.plantName = pe.plantName
        LEFT JOIN effects e ON pe.effectName = e.effectName
        WHERE i.userID = ?
        GROUP BY p.plantName, p.rarity, p.rarityID, p.plantDescription, i.quantity
        ORDER BY {filterReference[filter]}
        """
        return db.query(sql, [id])

    return result


def get_plants_by(keyword, filter):
    sql = f"""SELECT 
                p.plantName,
                p.rarity,
                p.rarityID,
                p.plantDescription,
                GROUP_CONCAT(DISTINCT a.areaName)   AS plantAreas,
                GROUP_CONCAT(DISTINCT r.regionName) AS plantRegions,
                GROUP_CONCAT(DISTINCT e.effectName) AS plantEffects
            FROM plants p
            JOIN area pa ON p.plantName = pa.plantName
            JOIN areas a ON pa.areaName = a.areaName
            JOIN region pr ON p.plantName = pr.plantName
            JOIN regions r ON pr.regionName = r.regionName
            JOIN effect pe ON p.plantName = pe.plantName
            JOIN effects e ON pe.effectName = e.effectName
            WHERE {filterReference[filter]} LIKE ?
            GROUP BY p.plantName, p.rarity, p.plantDescription
            ORDER BY {filterReference[filter]}
    """
    result = db.query(sql, ["%"+keyword+"%"])
    if keyword == "":
        sql = f"""SELECT 
            p.plantName,
            p.rarity,
            p.rarityID,
            p.plantDescription,
            GROUP_CONCAT(DISTINCT a.areaName)   AS plantAreas,
            GROUP_CONCAT(DISTINCT r.regionName) AS plantRegions,
            GROUP_CONCAT(DISTINCT e.effectName) AS plantEffects
            FROM plants p
            JOIN area pa ON p.plantName = pa.plantName
            JOIN areas a ON pa.areaName = a.areaName
            JOIN region pr ON p.plantName = pr.plantName
            JOIN regions r ON pr.regionName = r.regionName
            JOIN effect pe ON p.plantName = pe.plantName
            JOIN effects e ON pe.effectName = e.effectName
            GROUP BY p.plantName, p.rarity, p.plantDescription
            ORDER BY {filterReference[filter]}
        """
        return db.query(sql)
    return result

def override_plant(plant, oldName):
    plantUpdate = """
    UPDATE plants
    SET plantName = ?, rarity = ?, rarityID = ?, plantDescription = ?
    WHERE plantName = ?
    """

    db.execute("DELETE FROM area WHERE plantName = ?", [oldName])
    db.execute("DELETE FROM region WHERE plantName = ?", [oldName])
    db.execute("DELETE FROM effect WHERE plantName = ?", [oldName])
    db.execute(plantUpdate, [plant["name"], plant["rarity"], rarity.check_rarity(plant["rarity"]), plant["Description"], oldName]) 

    for a in plant["Area"]:
        db.execute("INSERT OR IGNORE INTO area (plantName, areaName) VALUES (?, ?)", [plant["name"], a])

    for r in plant["Region"]:
        db.execute("INSERT OR IGNORE INTO region (plantName, regionName) VALUES (?, ?)", [plant["name"], r])

    for e in plant["Effects"]:
        value = 0
        repeats = db.query("SELECT repeats FROM effect WHERE plantName = ? AND effectName = ?", [plant["name"], e])
        if repeats:
            value = repeats[0][0]+1
        db.execute("INSERT OR IGNORE INTO effect (plantName, effectName, repeats) VALUES (?, ?, ?)", [plant["name"], e, value])

def insert_plant(plant):
    plantInsert = "INSERT INTO plants (plantName, rarity, rarityID, plantDescription) VALUES (?,?,?,?)"
    db.execute(plantInsert, [plant["name"], plant["rarity"], rarity.check_rarity(plant["rarity"]), plant["Description"]])

    for i in plant["Area"]:
        sql = "INSERT OR IGNORE INTO areas (areaName) VALUES (?)"
        db.execute(sql, [i])
        sql = "INSERT INTO area (plantName, areaName) VALUES (?, ?)"
        db.execute(sql, [plant["name"], i])

    for i in plant["Region"]:
        sql = "INSERT OR IGNORE INTO regions (regionName) VALUES (?)"
        db.execute(sql, [i])
        sql = "INSERT INTO region (plantName, regionName) VALUES (?, ?)"
        db.execute(sql, [plant["name"], i])

    for i in plant["Effects"]:
        sql = "INSERT OR IGNORE INTO effects (effectName) VALUES (?)"
        db.execute(sql, [i])
        value = 0
        repeats = db.query("SELECT repeats FROM effect WHERE plantName = ? AND effectName = ?", [plant["name"], i])
        if repeats:
            value = repeats[0][0]+1
        db.execute("INSERT OR IGNORE INTO effect (plantName, effectName, repeats) VALUES (?, ?, ?)", [plant["name"], i, value])

def add_to_inventory(plant, user_id):
    result = db.query("SELECT quantity FROM inventory WHERE userID = ? AND plantName = ?", [user_id, plant["plantName"]])
    if result:
        quantity = result[0][0] + 1
        db.execute("UPDATE inventory SET quantity = ? WHERE userID = ? AND plantName = ?", [quantity, user_id, plant["plantName"]])
    else:
        db.execute("INSERT INTO inventory (userID, plantName, quantity) VALUES (?, ?, ?)", [user_id, plant["plantName"], 1])

def delete_plant(name):
    db.execute("DELETE FROM plants WHERE plantName = ?", [name])

def new_folder(id, name):
    sql = """
    INSERT INTO folders (userID, folderName) VALUES (?, ?)
    """
    db.execute(sql, [id, name])

def get_folder_plants(userID, folderName):
    folderID = db.query("SELECT folderID FROM folders WHERE userID = ? AND folderName = ?", [userID, folderName])[0][0]
    sql = """
    SELECT p.plantName, fp.quantity
    FROM folder fp
    JOIN plants p ON fp.plantName = p.plantName
    WHERE fp.folderID = ?
    """
    return db.query(sql, [folderID])

def move_plant_to_folder(userID, folderName, plantName):
    folder_rows = db.query("SELECT folderID FROM folders WHERE userID = ? AND folderName = ?", [userID, folderName])
    folderID = folder_rows[0][0]
    folder_contents = db.query("SELECT * FROM folder WHERE plantName = ? AND folderID = ?", [plantName, folderID])

    if folder_contents:
        sql =  """
        UPDATE folder SET quantity = quantity + 1
        WHERE folderID = ? AND plantName = ?
        """
        db.execute(sql, [folderID, plantName])
    else:
        sql =  """
        INSERT INTO folder (folderID, plantName, quantity)
        VALUES (?,?,1)
        """
        db.execute(sql, [folderID, plantName])
    
    plantQuantity = db.query("SELECT quantity FROM inventory WHERE userID = ? AND plantName = ?", [userID, plantName])
    current_quantity = plantQuantity[0][0]
    new_quantity = current_quantity - 1
    
    if new_quantity > 0:
        sql = """
        UPDATE inventory 
        SET quantity = ? 
        WHERE userID = ? AND plantName = ?
        """
        db.execute(sql, [new_quantity, userID, plantName])
    else:
        sql = """
        DELETE FROM inventory 
        WHERE userID = ? AND plantName = ?
        """
        db.execute(sql, [userID, plantName])

def get_folders(userID):
    folder_rows = db.query("SELECT * FROM folders WHERE userID = ?", [userID])
    sql_count = "SELECT quantity FROM folder WHERE folderID = ?"
    folders = {}
    for folder in folder_rows:
        folderName = folder["folderName"]
        folderID = folder["folderID"]
        quantities = db.query(sql_count, [folderID])
        count = 0
        for q in quantities:
            count += q[0]
        folders[folderName] = count
    return folders
