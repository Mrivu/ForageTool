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