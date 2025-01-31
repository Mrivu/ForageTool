import db

def get_plants():
    sql = "SELECT * FROM plants"
    return db.query(sql)

def get_plant(name):
    sql = "SELECT * FROM plants WHERE Name = ?"
    return db.query(sql, [name])[0]