import db
import config

filterReference = {
            "Name": "p.plantName",
            "Rarity": "p.rarityID",
            "Description": "p.plantDescription",
            "Area": "a.areaName",
            "Region": "r.regionName",
            "Effects": "e.effectName"
    }

def get_plant(name, id=None):
    if id != None:
        name = db.query("SELECT plantName FROM plants WHERE plantID = ?", [id])[0]["plantName"]
    sql = """
    SELECT 
        p.plantName,
        ra.rarity,
        p.rarityID,
        p.plantDescription,
        p.unobtainable,
        p.isHidden,
        p.isSecret,
        p.plantID,
        GROUP_CONCAT(DISTINCT a.areaName) AS plantAreas,
        GROUP_CONCAT(DISTINCT reg.regionName) AS plantRegions,
        (SELECT GROUP_CONCAT(effectName) 
         FROM effect 
         WHERE plantName = p.plantName) AS plantEffects
    FROM plants p
    JOIN rarity ra ON p.rarityID = ra.rarityID
    JOIN area pa ON p.plantName = pa.plantName
    JOIN areas a ON pa.areaName = a.areaName
    JOIN region pr ON p.plantName = pr.plantName
    JOIN regions reg ON pr.regionName = reg.regionName
    JOIN effect pe ON p.plantName = pe.plantName
    JOIN effects e ON pe.effectName = e.effectName
    WHERE p.plantName = ?
    GROUP BY p.plantName, ra.rarity, p.plantDescription
    """
    plant = db.query(sql, [name])
    if plant:
        return plant[0]
    return None

def is_plant(name):
    sql = """SELECT * FROM plants WHERE plantName = ?"""
    return db.query(sql, [name])

def get_inventory(user_id, keyword, filter, pageNum=None):
    base_sql = """
    SELECT 
        p.plantName,
        ra.rarity,
        p.rarityID,
        p.plantDescription,
        p.unobtainable,
        p.isHidden,
        p.isSecret,
        p.plantID,
        GROUP_CONCAT(DISTINCT a.areaName) AS plantAreas,
        GROUP_CONCAT(DISTINCT r.regionName) AS plantRegions,
        (SELECT GROUP_CONCAT(effectName) 
         FROM effect 
         WHERE plantName = p.plantName) AS plantEffects,
        i.quantity
    FROM inventory i
    JOIN plants p ON i.plantName = p.plantName
    JOIN rarity ra ON p.rarityID = ra.rarityID
    LEFT JOIN area pa ON p.plantName = pa.plantName
    LEFT JOIN areas a ON pa.areaName = a.areaName
    LEFT JOIN region pr ON p.plantName = pr.plantName
    LEFT JOIN regions r ON pr.regionName = r.regionName
    LEFT JOIN effect pe ON p.plantName = pe.plantName
    LEFT JOIN effects e ON pe.effectName = e.effectName
    WHERE i.userID = ?
    """
    
    arguments = [user_id]
    if keyword:
        base_sql += f" AND {filterReference[filter]} LIKE ?"
        arguments.append("%" + keyword + "%")
    
    
    base_sql += f"""
    GROUP BY p.plantName, ra.rarity, p.rarityID, p.plantDescription, i.quantity
    ORDER BY {filterReference[filter]}
    """
    if pageNum:
        limit = config.page_size
        offset = config.page_size * (pageNum - 1)
        base_sql += "LIMIT ? OFFSET ?"
        arguments.append(limit)
        arguments.append(offset)
    return db.query(base_sql, arguments)

def get_plants_by(keyword="", filter="Name", pageNum=None):
    if filter == "Rarity":
        whereClause = "ra.rarity LIKE ?"
        orderClause = "p.rarityID"
    else:
        whereClause = f"{filterReference[filter]} LIKE ?"
        orderClause = f"{filterReference[filter]}"
    
    base_sql = f"""SELECT 
                p.plantName,
                ra.rarity,
                p.rarityID,
                p.plantDescription,
                p.unobtainable,
                p.isHidden,
                p.isSecret,
                p.plantID,
                GROUP_CONCAT(DISTINCT a.areaName)   AS plantAreas,
                GROUP_CONCAT(DISTINCT r.regionName) AS plantRegions,
                (SELECT GROUP_CONCAT(effectName) 
                 FROM effect 
                 WHERE plantName = p.plantName) AS plantEffects
            FROM plants p
            JOIN rarity ra ON p.rarityID = ra.rarityID
            JOIN area pa ON p.plantName = pa.plantName
            JOIN areas a ON pa.areaName = a.areaName
            JOIN region pr ON p.plantName = pr.plantName
            JOIN regions r ON pr.regionName = r.regionName
            JOIN effect pe ON p.plantName = pe.plantName
            JOIN effects e ON pe.effectName = e.effectName """
    
    arguments = []
    if keyword:
        arguments.append("%" + keyword + "%")
        sql = f"""{base_sql}
            WHERE {whereClause}
            GROUP BY p.plantName, ra.rarity, p.plantDescription
            ORDER BY {orderClause}
        """
        if pageNum:
            limit = config.page_size
            offset = config.page_size * (pageNum - 1)
            sql += "LIMIT ? OFFSET ?"
            arguments.append(limit)
            arguments.append(offset)
        result = db.query(sql, arguments)
    else:
        sql = f"""{base_sql}
            GROUP BY p.plantName, ra.rarity, p.plantDescription
            ORDER BY {orderClause}
        """
        if pageNum:
            limit = config.page_size
            offset = config.page_size * (pageNum - 1)
            sql += "LIMIT ? OFFSET ?"
            arguments.append(limit)
            arguments.append(offset)
        result = db.query(sql, arguments)
    return result

def get_rarity(plantName=None):
    if plantName is None:
        return [row[0] for row in db.query("SELECT rarity FROM rarity")] ## ["rarity"], ["rartyID"]
    else:
        rarityID = db.query("SELECT rarityID FROM plants WHERE plantName = ?", [plantName])
        return db.query("SELECT rarity FROM rarity WHERE rarityID = ?", [rarityID])

def new_plantID():
    largestID = db.query("SELECT plantID FROM plants ORDER BY plantID DESC LIMIT 1")
    if largestID:
        return largestID[0][0]+1
    return 1

def override_plant(plant, oldName, attributes=[0,0,0]):
    plantUpdate = """
    UPDATE plants
    SET plantName = ?, rarityID = ?, plantDescription = ?, unobtainable = ?, isHidden = ?, isSecret = ?
    WHERE plantName = ?
    """

    rarityID = -1
    if plant["rarity"] in get_rarity():
        rarityID = db.query("SELECT rarityID FROM rarity WHERE rarity = ?", [plant["rarity"]])[0][0]

    db.execute("DELETE FROM area WHERE plantName = ?", [oldName])
    db.execute("DELETE FROM region WHERE plantName = ?", [oldName])
    db.execute("DELETE FROM effect WHERE plantName = ?", [oldName])
    db.execute(plantUpdate, [plant["name"], rarityID, plant["Description"], attributes[0], attributes[1], attributes[2], oldName]) 

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
    plantInsert = "INSERT OR IGNORE INTO plants (plantName, rarityID, plantDescription, plantID) VALUES (?,?,?,?)"

    rarityID = -1
    if plant["rarity"] in get_rarity():
        rarityID = db.query("SELECT rarityID FROM rarity WHERE rarity = ?", [plant["rarity"]])[0][0]

    db.execute(plantInsert, [plant["name"], rarityID, plant["Description"], new_plantID()])

    for i in plant["Area"]:
        sql = "INSERT OR IGNORE INTO areas (areaName) VALUES (?)"
        db.execute(sql, [i])
        sql = "INSERT OR IGNORE INTO area (plantName, areaName) VALUES (?, ?)"
        db.execute(sql, [plant["name"], i])

    for i in plant["Region"]:
        sql = "INSERT OR IGNORE INTO regions (regionName) VALUES (?)"
        db.execute(sql, [i])
        sql = "INSERT OR IGNORE INTO region (plantName, regionName) VALUES (?, ?)"
        db.execute(sql, [plant["name"], i])

    for i in plant["Effects"]:
        sql = "INSERT OR IGNORE INTO effects (effectName) VALUES (?)"
        db.execute(sql, [i])
        value = 0
        repeats = db.query("SELECT repeats FROM effect WHERE plantName = ? AND effectName = ?", [plant["name"], i])
        if repeats:
            value = repeats[0][0]+1
        db.execute("INSERT OR IGNORE INTO effect (plantName, effectName, repeats) VALUES (?, ?, ?)", [plant["name"], i, value])

def add_to_inventory(plant, user_id, count=1):
    db.execute("INSERT OR IGNORE INTO found (plantName, userID) VALUES (?, ?)", [plant["plantName"], user_id])
    result = db.query("SELECT quantity FROM inventory WHERE userID = ? AND plantName = ?", [user_id, plant["plantName"]])
    if result:
        quantity = result[0][0] + count
        db.execute("UPDATE inventory SET quantity = ? WHERE userID = ? AND plantName = ?", [quantity, user_id, plant["plantName"]])
    else:
        db.execute("INSERT INTO inventory (userID, plantName, quantity) VALUES (?, ?, ?)", [user_id, plant["plantName"], count])

def get_found(user_id):
    return db.query("SELECT plantName FROM found WHERE userID = ?", [user_id])

def remove_from_inventory(userID, plantName, change=1):
    plantQuantity = db.query("SELECT quantity FROM inventory WHERE userID = ? AND plantName = ?", [userID, plantName])
    current_quantity = plantQuantity[0][0]
    new_quantity = current_quantity - change
    
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
    

def forage_plant(rarityID, area, region):
    sql = """
    SELECT p.plantName, p.rarityID
    FROM plants p
    JOIN area a ON p.plantName = a.plantName
    JOIN region r ON p.plantName = r.plantName
    WHERE p.rarityID = ? AND a.areaName = ? AND r.regionName = ? AND p.unobtainable = 0
    ORDER BY RANDOM() LIMIT 1
    """
    return db.query(sql, [rarityID, area, region])
        

def delete_plant(name):
    db.execute("DELETE FROM plants WHERE plantName = ?", [name])

def new_folder(id, name):
    sql = """
    INSERT OR IGNORE INTO folders (userID, folderName) VALUES (?, ?)
    """
    db.execute(sql, [id, name])

def get_folder_plants(userID, folderName, keyword="", filter="Name", pageNum=None):
    folder_rows = db.query("SELECT folderID FROM folders WHERE userID = ? AND folderName = ?", [userID, folderName])
    folderID = folder_rows[0][0]
    
    base_sql = """
    SELECT 
        p.plantName, 
        fp.quantity,
        ra.rarity,
        p.rarityID,
        p.plantDescription,
        GROUP_CONCAT(DISTINCT a.areaName) AS plantAreas,
        GROUP_CONCAT(DISTINCT r.regionName) AS plantRegions,
        (SELECT GROUP_CONCAT(effectName) 
         FROM effect 
         WHERE plantName = p.plantName) AS plantEffects
    FROM folder fp
    JOIN plants p ON fp.plantName = p.plantName
    JOIN rarity ra ON p.rarityID = ra.rarityID
    LEFT JOIN area pa ON p.plantName = pa.plantName
    LEFT JOIN areas a ON pa.areaName = a.areaName
    LEFT JOIN region pr ON p.plantName = pr.plantName
    LEFT JOIN regions r ON pr.regionName = r.regionName
    LEFT JOIN effect pe ON p.plantName = pe.plantName
    LEFT JOIN effects e ON pe.effectName = e.effectName
    WHERE fp.folderID = ?
    """
    
    arguments = [folderID]
    if keyword:
        if filter == "Rarity":
            whereClause = "ra.rarity LIKE ?"
        else:
            whereClause = f"{filterReference[filter]} LIKE ?"
        base_sql += " AND " + whereClause
        arguments.append("%" + keyword + "%")
    
    base_sql += """
    GROUP BY p.plantName, ra.rarity, p.rarityID, p.plantDescription, fp.quantity
    """
    base_sql += f" ORDER BY {filterReference[filter]}"
    
    if pageNum:
        limit = config.page_size
        offset = config.page_size * (pageNum - 1)
        base_sql += " LIMIT ? OFFSET ?"
        arguments.append(limit)
        arguments.append(offset)

    return db.query(base_sql, arguments)

def move_plant_to_folder(userID, folderName, plantName, change=1):
    folder_rows = db.query("SELECT folderID FROM folders WHERE userID = ? AND folderName = ?", [userID, folderName])
    if not folder_rows:
        raise ValueError(f"Folder '{folderName}' not found for user {userID}")
    folderID = folder_rows[0][0]
    folder_contents = db.query("SELECT quantity FROM folder WHERE plantName = ? AND folderID = ?", [plantName, folderID])

    if folder_contents:
        sql =  """
        UPDATE folder SET quantity = quantity + ?
        WHERE folderID = ? AND plantName = ?
        """
        db.execute(sql, [change, folderID, plantName])
    else:
        sql =  """
        INSERT INTO folder (folderID, plantName, quantity)
        VALUES (?,?,?)
        """
        db.execute(sql, [folderID, plantName, change])
    
    plantQuantity = db.query("SELECT quantity FROM inventory WHERE userID = ? AND plantName = ?", [userID, plantName])
    current_quantity = plantQuantity[0][0]
    new_quantity = current_quantity - change
    
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

def unfolder(userID, folderName, plantName, change=1):
    folder_rows = db.query("SELECT folderID FROM folders WHERE userID = ? AND folderName = ?", [userID, folderName])
    if not folder_rows:
        raise ValueError(f"Folder '{folderName}' not found for user {userID}")
    folderID = folder_rows[0][0]
    folder_quantity = db.query("SELECT quantity FROM folder WHERE plantName = ? AND folderID = ?", [plantName, folderID])[0][0]

    inventory_quanity = db.query("SELECT quantity FROM inventory WHERE userID = ? AND plantName = ?", [userID, plantName])

    if inventory_quanity:
        sql = """
        UPDATE inventory 
        SET quantity = ? 
        WHERE userID = ? AND plantName = ?
        """
        db.execute(sql, [inventory_quanity[0][0]+change, userID, plantName])
    else:
        sql = """
        INSERT INTO inventory (quantity, userID, plantName) VALUES (?,?,?)
        """
        db.execute(sql, [change, userID, plantName])

    if folder_quantity > 1:
        sql =  """
        UPDATE folder SET quantity = quantity - ?
        WHERE folderID = ? AND plantName = ?
        """
        db.execute(sql, [change, folderID, plantName])
    else:
        sql = """
        DELETE FROM folder 
        WHERE folderID = ? AND plantName = ?
        """
        db.execute(sql, [folderID, plantName])
    
def get_folders(userID):
    folder_rows = db.query("SELECT folderID, folderName FROM folders WHERE userID = ?", [userID])
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

def delete_folder(userID, name):
    target_folder = db.query("SELECT folderID, folderName FROM folders WHERE userID = ? AND folderName = ?", [userID, name])
    for i in get_folder_plants(userID, name):
        unfolder(userID, name, i["plantName"], i["quantity"])
    sql = "DELETE FROM folders WHERE userID = ? AND folderName = ? AND folderID = ?"
    db.execute(sql, [userID, name, target_folder[0]["folderID"]])

def rename_folder(userID, name, newName):
    target_folder = db.query("SELECT folderID, folderName FROM folders WHERE userID = ? AND folderName = ?", [userID, name])
    rename = """UPDATE folders SET folderName = ? WHERE folderID = ? AND userID = ?"""
    db.execute(rename, [newName, target_folder[0]["folderID"], userID])

