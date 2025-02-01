import db

def get_plants():
    sql = "SELECT * FROM plants"
    return db.query(sql)

def get_plant(name):
    sql = "SELECT * FROM plants WHERE Name = ?"
    result = db.query(sql, [name])
    if result:
        return result[0]
    return None

def get_plants_by(keyword, filter):
    match filter:
        case "Name":
            sql = "SELECT * FROM plants WHERE Name LIKE ? ORDER BY Name"
        case "Rarity":
            sql = "SELECT * FROM plants WHERE Rarity LIKE ? ORDER BY Rarity"
        case "Area":
            sql = "SELECT * FROM plants WHERE Area LIKE ? ORDER BY Area"
        case "Region":
            sql = "SELECT * FROM plants WHERE Region LIKE ? ORDER BY Region"
        case "Effects":
            sql = "SELECT * FROM plants WHERE Effects LIKE ? ORDER BY Effects"
        case "Description":
            sql = "SELECT * FROM plants WHERE Description LIKE ? ORDER BY Description"
    result = db.query(sql, ["%"+keyword+"%"])
    if keyword == "":
        sql = f"SELECT * FROM plants ORDER BY {filter}"
        return db.query(sql)
    return result

        


