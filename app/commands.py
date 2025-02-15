import db
import rarity

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

def get_plants_by(keyword, filter):
    filterReference = {
            "Name": "p.plantName",
            "Rarity": "p.rarityID",
            "Description": "p.plantDescription",
            "Area": "a.areaName",
            "Region": "r.regionName",
            "Effects": "e.effectName"
    }
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

def override_plant(plant):
    plantUpdate = """
    UPDATE plants
    SET plantName = ?, rarity = ?, rarityID = ?, plantDescription = ?
    WHERE plantName = ?
    """

    db.execute("DELETE FROM area WHERE plantName = ?", [plant["oldName"]])
    db.execute("DELETE FROM region WHERE plantName = ?", [plant["oldName"]])
    db.execute("DELETE FROM effect WHERE plantName = ?", [plant["oldName"]])
    db.execute(plantUpdate, [plant["name"], plant["rarity"], rarity.check_rarity(plant["rarity"]), plant["Description"], plant["oldName"]]) 

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

def delete_plant(name):
    db.execute("DELETE FROM plants WHERE plantName = ?", [name])
