import db

def get_plants():
    sql = "SELECT * FROM plants"
    return db.query(sql)