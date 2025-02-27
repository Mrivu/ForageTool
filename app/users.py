from werkzeug.security import check_password_hash, generate_password_hash
import db
from flask import session, abort, redirect, render_template
import sqlite3

def require_login():
    if "userID" not in session:
        return abort(403)

def require_admin():
    if not session["isAdmin"]:
        abort(403)

def logout():
    session.clear()
    return redirect("/")
    
def login(username, password):
    sql_password = "SELECT password_hash FROM users WHERE username = ?"
    password_hash = db.query(sql_password, [username])
    if password_hash:
        password_hash = password_hash[0][0]
        if check_password_hash(password_hash, password):
            session["username"] = username
            getAdminStatus = "SELECT isAdmin FROM users WHERE username = ?"
            isAdmin = db.query(getAdminStatus, [username])
            session["isAdmin"] = isAdmin[0][0]
            getID = db.query("SELECT userID FROM users where username = ?", [session["username"]])
            session["userID"] = getID[0][0]
            bonus = db.query("SELECT forageBonus FROM users where username = ?", [session["username"]])
            session["forageBonus"] = bonus[0][0]
            multiplier = db.query("SELECT forageMultiplier FROM users where username = ?", [session["username"]])
            session["forageMultiplier"] = multiplier[0][0]
            return redirect("/")
        
def register_user(username, password1, password2, bonus, multiplier, isAdmin):
    isAdmin = 0 if isAdmin == "no" else 1
    if password1 != password2:
        return render_template("register.html", message = "The passwords don't match")
    password_hash = generate_password_hash(password1)
    try:
        sql = "INSERT INTO users (username, password_hash, isAdmin, forageBonus, forageMultiplier) VALUES (?, ?, ?, ?, ?)"
        db.execute(sql, [username, password_hash, isAdmin, bonus, multiplier])
    except sqlite3.IntegrityError:
        return render_template("register.html", message = f"The username {username} is aready taken")
    session["username"] = username
    session["isAdmin"] = isAdmin
    session["forageBonus"] = bonus
    session["forageMultiplier"] = multiplier
    getID = db.query("SELECT userID FROM users where username = ?", [session["username"]])
    session["userID"] = getID[0][0]
    db.execute("INSERT INTO statistics (userID) VALUES (?)", [session["userID"]])
